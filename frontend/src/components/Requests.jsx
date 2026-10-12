import { useEffect, useState } from 'react';
import { api, BLOOD_GROUPS, COMPONENTS, formatDate, label, URGENCIES } from '../api.js';
import { Empty, Field, GroupBadge, Modal, Pill, Select } from './ui.jsx';

const EMPTY_REQUEST = { hospital: '', patient_ref: '', blood_group: 'A+', component: 'RED_CELLS', units_needed: 1, urgency: 'ROUTINE', notes: '' };

function RequestForm({ onSave, onClose }) {
  const [form, setForm] = useState(EMPTY_REQUEST);
  const [compat, setCompat] = useState(null);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const set = (key) => (v) => setForm((f) => ({ ...f, [key]: v?.target ? v.target.value : v }));

  useEffect(() => {
    let live = true;
    api.compatibility(form.blood_group, form.component).then((c) => live && setCompat(c)).catch(() => live && setCompat(null));
    return () => { live = false; };
  }, [form.blood_group, form.component]);

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave({ ...form, units_needed: Number(form.units_needed) });
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  };

  return (
    <Modal title="New hospital request" onClose={onClose}>
      <form className="form" onSubmit={submit}>
        <div className="row">
          <Field label="Hospital"><input required value={form.hospital} onChange={set('hospital')} /></Field>
          <Field label="Patient reference"><input required value={form.patient_ref} onChange={set('patient_ref')} placeholder="e.g. ICU-2231" /></Field>
        </div>
        <div className="row three">
          <Field label="Patient group"><Select value={form.blood_group} onChange={set('blood_group')} options={BLOOD_GROUPS} /></Field>
          <Field label="Component"><Select value={form.component} onChange={set('component')} options={COMPONENTS} /></Field>
          <Field label="Units"><input type="number" min="1" max="20" value={form.units_needed} onChange={set('units_needed')} /></Field>
        </div>
        {compat && (
          <div className={`compat ${compat.available_units >= form.units_needed ? 'ok' : 'short'}`}>
            <span>Compatible donors:</span>
            <span className="compat-groups">{compat.compatible_donor_groups.map((g) => <GroupBadge key={g} group={g} />)}</span>
            <b>{compat.available_units} unit{compat.available_units === 1 ? '' : 's'} in stock</b>
          </div>
        )}
        <Field label="Urgency">
          <div className="segmented">
            {URGENCIES.map((u) => (
              <button type="button" key={u} className={form.urgency === u ? `on ${u.toLowerCase()}` : ''} onClick={() => set('urgency')(u)}>{label(u)}</button>
            ))}
          </div>
        </Field>
        <Field label="Notes"><textarea rows="2" value={form.notes} onChange={set('notes')} /></Field>
        {error && <p className="form-error">{error}</p>}
        <footer className="form-actions">
          <button type="button" className="btn ghost" onClick={onClose}>Cancel</button>
          <button className="btn" disabled={saving}>{saving ? 'Saving…' : 'Create request'}</button>
        </footer>
      </form>
    </Modal>
  );
}

export default function Requests({ requests, onFulfil, busyId, notify, reload }) {
  const [status, setStatus] = useState('');
  const [creating, setCreating] = useState(false);
  const shown = (requests ?? []).filter((r) => !status || r.status === status);

  const create = async (body) => {
    await api.createRequest(body);
    setCreating(false);
    notify('Request logged');
    reload();
  };

  const cancel = async (r) => {
    if (!confirm(`Cancel request ${r.patient_ref} from ${r.hospital}?`)) return;
    try {
      await api.updateRequest(r.id, { status: 'CANCELLED' });
      notify('Request cancelled');
      reload();
    } catch (err) {
      notify(err.message, 'error');
    }
  };

  return (
    <section className="card">
      <header className="card-head wrap">
        <h2>Hospital requests</h2>
        <div className="toolbar">
          <Select value={status} onChange={setStatus} options={['PENDING', 'PARTIAL', 'FULFILLED', 'CANCELLED']} placeholder="All statuses" />
          <button className="btn" onClick={() => setCreating(true)}>+ New request</button>
        </div>
      </header>

      {requests === null ? (
        <div className="skeleton" />
      ) : shown.length === 0 ? (
        <Empty>No requests here yet.</Empty>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Patient</th><th>Need</th><th>Progress</th><th>Urgency</th><th>Status</th><th aria-label="Actions" /></tr>
            </thead>
            <tbody>
              {shown.map((r) => {
                const open = r.status === 'PENDING' || r.status === 'PARTIAL';
                return (
                  <tr key={r.id}>
                    <td data-label="Patient"><strong>{r.patient_ref}</strong><small>{r.hospital} · {formatDate(r.created_at)}</small></td>
                    <td data-label="Need"><GroupBadge group={r.blood_group} /> {label(r.component)}</td>
                    <td data-label="Progress">
                      <div className="progress" title={`${r.units_issued} of ${r.units_needed} issued`}>
                        <span style={{ width: `${(r.units_issued / r.units_needed) * 100}%` }} />
                      </div>
                      <small>{r.units_issued}/{r.units_needed} units</small>
                    </td>
                    <td data-label="Urgency"><Pill value={r.urgency} /></td>
                    <td data-label="Status"><Pill value={r.status} /></td>
                    <td className="actions">
                      {open && (
                        <>
                          <button className="btn sm" disabled={busyId === r.id} onClick={() => onFulfil(r)}>{busyId === r.id ? '…' : 'Fulfil'}</button>
                          <button className="btn sm ghost" onClick={() => cancel(r)}>Cancel</button>
                        </>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
      {creating && <RequestForm onSave={create} onClose={() => setCreating(false)} />}
    </section>
  );
}
