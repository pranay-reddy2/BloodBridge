import { label } from '../api.js';
import { Empty, GroupBadge, Pill } from './ui.jsx';

function Kpi({ title, value, sub, tone }) {
  return (
    <div className={`kpi ${tone ?? ''}`}>
      <span className="kpi-title">{title}</span>
      <strong className="kpi-value">{value}</strong>
      <span className="kpi-sub">{sub}</span>
    </div>
  );
}

export default function Overview({ summary, openRequests, onFulfil, busyId, goTo }) {
  if (!summary) return null;
  const threshold = summary.low_stock_threshold;
  const scale = Math.max(threshold * 3, ...summary.by_blood_group.map((g) => g.available), 1);
  const lowGroups = summary.by_blood_group.filter((g) => g.low_stock).map((g) => g.blood_group);
  const totalComponents = Math.max(1, ...Object.values(summary.by_component));

  return (
    <>
      <section className="kpis">
        <Kpi title="Units in stock" value={summary.available_units} sub="usable, unexpired" />
        <Kpi
          title="Eligible donors"
          value={summary.eligible_donors}
          sub={`of ${summary.total_donors} registered`}
        />
        <Kpi
          title="Open requests"
          value={summary.pending_requests}
          sub={`${summary.critical_requests} critical`}
          tone={summary.critical_requests ? 'danger' : ''}
        />
        <Kpi
          title="Expiring in 7 days"
          value={summary.expiring_soon}
          sub="use these first"
          tone={summary.expiring_soon ? 'warn' : ''}
        />
      </section>

      {lowGroups.length > 0 && (
        <div className="banner warn">
          <strong>Low stock:</strong> {lowGroups.join(', ')} below {threshold} units — consider a donor call-out.
        </div>
      )}

      <div className="grid-2">
        <section className="card">
          <header className="card-head">
            <h2>Stock by blood group</h2>
            <button className="link-btn" onClick={() => goTo('inventory')}>View units →</button>
          </header>
          <div className="stock-grid">
            {summary.by_blood_group.map((g) => (
              <div key={g.blood_group} className={`stock-tile ${g.low_stock ? 'low' : ''}`}>
                <div className="stock-top">
                  <GroupBadge group={g.blood_group} />
                  <span className="stock-count">{g.available}</span>
                </div>
                <div className="meter" aria-hidden="true">
                  <span style={{ width: `${(g.available / scale) * 100}%` }} />
                  <i style={{ left: `${(threshold / scale) * 100}%` }} />
                </div>
                <small>{g.expiring_soon ? `${g.expiring_soon} expiring soon` : g.low_stock ? 'Low stock' : 'Healthy'}</small>
              </div>
            ))}
          </div>
          <div className="components">
            {Object.entries(summary.by_component).map(([name, count]) => (
              <div key={name} className="component-row">
                <span>{label(name)}</span>
                <div className="bar"><span style={{ width: `${(count / totalComponents) * 100}%` }} /></div>
                <b>{count}</b>
              </div>
            ))}
          </div>
        </section>

        <section className="card">
          <header className="card-head">
            <h2>Request queue</h2>
            <button className="link-btn" onClick={() => goTo('requests')}>All requests →</button>
          </header>
          {openRequests.length === 0 ? (
            <Empty>No open requests. 🎉</Empty>
          ) : (
            <ul className="queue">
              {openRequests.slice(0, 6).map((r) => (
                <li key={r.id} className={`queue-item ${r.urgency.toLowerCase()}`}>
                  <div>
                    <div className="queue-title">
                      <GroupBadge group={r.blood_group} /> {r.units_needed - r.units_issued} × {label(r.component)}
                    </div>
                    <small>{r.hospital} · {r.patient_ref}</small>
                  </div>
                  <div className="queue-actions">
                    <Pill value={r.urgency} />
                    <button className="btn sm" disabled={busyId === r.id} onClick={() => onFulfil(r)}>
                      {busyId === r.id ? '…' : 'Fulfil'}
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </>
  );
}
