import { useCallback, useEffect, useState } from 'react';
import { api, label } from './api.js';
import Donors from './components/Donors.jsx';
import Inventory from './components/Inventory.jsx';
import Overview from './components/Overview.jsx';
import Requests from './components/Requests.jsx';

const PAGES = [
  { id: 'overview', title: 'Overview', icon: '◎' },
  { id: 'donors', title: 'Donors', icon: '♥' },
  { id: 'requests', title: 'Requests', icon: '✚' },
  { id: 'inventory', title: 'Inventory', icon: '▤' },
];

const REFRESH_MS = 15_000;
let toastSeq = 0; // crypto.randomUUID() is unavailable on plain-HTTP Ingress hosts

export default function App() {
  const [page, setPage] = useState(() => location.hash.slice(1) || 'overview');
  const [summary, setSummary] = useState(null);
  const [requests, setRequests] = useState(null);
  const [meta, setMeta] = useState(null);
  const [apiDown, setApiDown] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [busyId, setBusyId] = useState(null);
  const [version, setVersion] = useState(0);

  const notify = useCallback((text, kind = 'ok') => {
    const id = ++toastSeq;
    setToasts((t) => [...t, { id, text, kind }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 4500);
  }, []);

  const refresh = useCallback(async () => {
    try {
      const [s, r] = await Promise.all([api.summary(), api.requests()]);
      setSummary(s);
      setRequests(r);
      setApiDown(false);
    } catch {
      setApiDown(true);
    }
  }, []);

  const changed = useCallback(() => {
    refresh();
    setVersion((v) => v + 1);
  }, [refresh]);

  useEffect(() => {
    refresh();
    api.meta().then(setMeta).catch(() => {});
    const timer = setInterval(refresh, REFRESH_MS);
    return () => clearInterval(timer);
  }, [refresh]);

  useEffect(() => {
    location.hash = page;
    const onHash = () => setPage(location.hash.slice(1) || 'overview');
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, [page]);

  const fulfil = async (r) => {
    setBusyId(r.id);
    try {
      const result = await api.fulfil(r.id);
      const groups = [...new Set(result.allocated_units.map((u) => u.blood_group))].join(', ');
      notify(
        result.shortfall
          ? `Issued ${result.allocated_units.length} unit(s) (${groups}); still short by ${result.shortfall}`
          : `Request fulfilled with ${result.allocated_units.length} unit(s) of ${groups}`,
        result.shortfall ? 'warn' : 'ok',
      );
      changed();
    } catch (err) {
      notify(err.message, 'error');
    } finally {
      setBusyId(null);
    }
  };

  const openRequests = (requests ?? []).filter((r) => r.status === 'PENDING' || r.status === 'PARTIAL');
  const current = PAGES.find((p) => p.id === page) ?? PAGES[0];

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2s7 7.6 7 12.5A7 7 0 0 1 5 14.5C5 9.6 12 2 12 2z" /></svg>
          <div>
            <strong>BloodBridge</strong>
            <small>Donor &amp; inventory network</small>
          </div>
        </div>
        <nav>
          {PAGES.map((p) => (
            <button key={p.id} className={p.id === current.id ? 'active' : ''} onClick={() => setPage(p.id)}>
              <span aria-hidden="true">{p.icon}</span>
              {p.title}
              {p.id === 'requests' && openRequests.length > 0 && <em>{openRequests.length}</em>}
            </button>
          ))}
        </nav>
        <footer className="build">
          <span className={`dot ${apiDown ? 'down' : 'up'}`} />
          {apiDown ? 'API unreachable' : 'API connected'}
          {meta && (
            <small title={`${meta.service} ${meta.version}`}>
              build {meta.version.slice(0, 7)} · {label(meta.environment)}
            </small>
          )}
        </footer>
      </aside>

      <main className="content">
        <header className="page-head">
          <div>
            <h1>{current.title}</h1>
            <p>{summary ? `Stock as of ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : 'Loading…'}</p>
          </div>
          <button className="btn ghost" onClick={changed}>↻ Refresh</button>
        </header>

        {apiDown && (
          <div className="banner danger">
            Cannot reach the BloodBridge API. Check that the backend pods are Ready
            (<code>kubectl get pods -n bloodbridge</code>) and try again.
          </div>
        )}
        {!summary && !apiDown && <div className="skeleton tall" />}

        {current.id === 'overview' && (
          <Overview summary={summary} openRequests={openRequests} onFulfil={fulfil} busyId={busyId} goTo={setPage} />
        )}
        {current.id === 'donors' && <Donors notify={notify} onChanged={changed} />}
        {current.id === 'requests' && (
          <Requests requests={requests} onFulfil={fulfil} busyId={busyId} notify={notify} reload={changed} />
        )}
        {current.id === 'inventory' && <Inventory notify={notify} onChanged={changed} version={version} />}
      </main>

      <div className="toasts" role="status" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.kind}`}>{t.text}</div>
        ))}
      </div>
    </div>
  );
}
