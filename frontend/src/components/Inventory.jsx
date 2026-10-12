import { useCallback, useEffect, useState } from 'react';
import { api, BLOOD_GROUPS, COMPONENTS, daysUntil, formatDate, label } from '../api.js';
import { Empty, GroupBadge, Pill, Select } from './ui.jsx';

function Expiry({ unit }) {
  if (!['AVAILABLE', 'QUARANTINED'].includes(unit.status)) return <span>{formatDate(unit.expires_on)}</span>;
  const days = daysUntil(unit.expires_on);
  const tone = days < 0 ? 'danger' : days <= 3 ? 'danger' : days <= 7 ? 'warn' : 'ok';
  const text = days < 0 ? 'expired' : days === 0 ? 'today' : `${days}d left`;
  return (
    <span className="expiry">
      {formatDate(unit.expires_on)} <span className={`chip ${tone}`}>{text}</span>
    </span>
  );
}

export default function Inventory({ notify, onChanged, version }) {
  const [units, setUnits] = useState(null);
  const [filters, setFilters] = useState({ status: 'AVAILABLE', blood_group: '', component: '' });

  const load = useCallback(async () => {
    try {
      setUnits(await api.units(filters));
    } catch (err) {
      notify(err.message, 'error');
    }
  }, [filters, notify]);

  useEffect(() => { load(); }, [load, version]);

  const setStatus = async (unit, status) => {
    try {
      await api.updateUnit(unit.id, status);
      notify(`Unit #${unit.id} marked ${label(status).toLowerCase()}`);
      load();
      onChanged();
    } catch (err) {
      notify(err.message, 'error');
    }
  };

  const sweep = async () => {
    try {
      const { expired } = await api.expireSweep();
      notify(expired ? `${expired} expired unit(s) removed from stock` : 'No expired units found');
      load();
      onChanged();
    } catch (err) {
      notify(err.message, 'error');
    }
  };

  return (
    <section className="card">
      <header className="card-head wrap">
        <h2>Blood units</h2>
        <div className="toolbar">
          <Select value={filters.status} onChange={(v) => setFilters({ ...filters, status: v })} options={['AVAILABLE', 'QUARANTINED', 'ISSUED', 'EXPIRED', 'DISCARDED']} placeholder="Any status" />
          <Select value={filters.blood_group} onChange={(v) => setFilters({ ...filters, blood_group: v })} options={BLOOD_GROUPS} placeholder="All groups" />
          <Select value={filters.component} onChange={(v) => setFilters({ ...filters, component: v })} options={COMPONENTS} placeholder="All components" />
          <button className="btn ghost" onClick={sweep} title="Mark every unit past its expiry date as EXPIRED">Run expiry sweep</button>
        </div>
      </header>

      {units === null ? (
        <div className="skeleton" />
      ) : units.length === 0 ? (
        <Empty>No units match. Record a donation from the Donors page to add stock.</Empty>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Unit</th><th>Group</th><th>Component</th><th>Collected</th><th>Expires</th><th>Status</th><th aria-label="Actions" /></tr>
            </thead>
            <tbody>
              {units.map((u) => (
                <tr key={u.id}>
                  <td data-label="Unit"><strong>#{String(u.id).padStart(5, '0')}</strong><small>{u.volume_ml} ml · donor {u.donor_id}</small></td>
                  <td data-label="Group"><GroupBadge group={u.blood_group} /></td>
                  <td data-label="Component">{label(u.component)}</td>
                  <td data-label="Collected">{formatDate(u.collected_on)}</td>
                  <td data-label="Expires"><Expiry unit={u} /></td>
                  <td data-label="Status"><Pill value={u.status} />{u.request_id && <small>request #{u.request_id}</small>}</td>
                  <td className="actions">
                    {u.status === 'AVAILABLE' && <button className="btn sm ghost" onClick={() => setStatus(u, 'QUARANTINED')}>Quarantine</button>}
                    {u.status === 'QUARANTINED' && daysUntil(u.expires_on) >= 0 && <button className="btn sm ghost" onClick={() => setStatus(u, 'AVAILABLE')}>Release</button>}
                    {['AVAILABLE', 'QUARANTINED'].includes(u.status) && <button className="btn sm ghost danger" onClick={() => setStatus(u, 'DISCARDED')}>Discard</button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
