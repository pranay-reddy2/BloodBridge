import { useCallback, useEffect, useState } from 'react';
import { api, BLOOD_GROUPS, COMPONENTS, formatDate, label } from '../api.js';
import { Empty, Field, GroupBadge, Modal, Pill, Select } from './ui.jsx';

const EMPTY_DONOR = { full_name: '', blood_group: 'O+', email: '', phone: '', city: '', last_donation_date: '' };
const DEFAULT_VOLUME = { WHOLE_BLOOD: 450, RED_CELLS: 280, PLASMA: 250, PLATELETS: 250 };

function DonorForm({ onSave, onClose }) {
  const [form, setForm] = useState(EMPTY_DONOR);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const set = (key) => (e) => setForm({ ...form, [key]: e.target ? e.target.value : e });

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await onSave({ ...form, last_donation_date: form.last_donation_date || null });
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  };

  return (
    <Modal title="Register donor" onClose={onClose}>
      <form className="form" onSubmit={submit}>
        <Field label="Full name"><input required value={form.full_name} onChange={set('full_name')} /></Field>
        <div className="row">
          <Field label="Blood group"><Select value={form.blood_group} onChange={set('blood_group')} options={BLOOD_GROUPS} /></Field>
          <Field label="City"><input required value={form.city} onChange={set('city')} /></Field>
        </div>
        <div className="row">
          <Field label="Email"><input required type="email" value={form.email} onChange={set('email')} /></Field>
          <Field label="Phone"><input required value={form.phone} onChange={set('phone')} placeholder="+91 98765 43210" /></Field>
        </div>
        <Field label="Last donation (optional)" hint="Used to compute the 90-day eligibility window.">
          <input type="date" value={form.last_donation_date} max={new Date().toISOString().slice(0, 10)} onChange={set('last_donation_date')} />
        </Field>
        {error && <p className="form-error">{error}</p>}
        <footer className="form-actions">
          <button type="button" className="btn ghost" onClick={onClose}>Cancel</button>
          <button className="btn" disabled={saving}>{saving ? 'Saving…' : 'Register donor'}</button>
        </footer>
      </form>
    </Modal>
  );
}

function DonationForm({ donor, onSave, onClose }) {
  const [component, setComponent] = useState('WHOLE_BLOOD');
  const [volume, setVolume] = useState(DEFAULT_VOLUME.WHOLE_BLOOD);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave({ component, volume_ml: Number(volume) });
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  };

  return (
    <Modal title={`Record donation — ${donor.full_name}`} onClose={onClose}>
      <form className="form" onSubmit={submit}>
        <p className="muted">Blood group <GroupBadge group={donor.blood_group} /> will be recorded on the unit.</p>
        <div className="row">
          <Field label="Component">
            <Select value={component} onChange={(v) => { setComponent(v); setVolume(DEFAULT_VOLUME[v]); }} options={COMPONENTS} />
          </Field>
          <Field label="Volume (ml)"><input type="number" min="50" max="600" value={volume} onChange={(e) => setVolume(e.target.value)} /></Field>
        </div>
        {error && <p className="form-error">{error}</p>}
        <footer className="form-actions">
          <button type="button" className="btn ghost" onClick={onClose}>Cancel</button>
          <button className="btn" disabled={saving}>{saving ? 'Saving…' : 'Record donation'}</button>
        </footer>
      </form>
    </Modal>
  );
}

export default function Donors({ notify, onChanged }) {
  const [donors, setDonors] = useState(null);
  const [filters, setFilters] = useState({ q: '', blood_group: '', eligible: '' });
  const [modal, setModal] = useState(null);

  const load = useCallback(async () => {
    try {
      setDonors(await api.donors(filters));
    } catch (err) {
      notify(err.message, 'error');
    }
  }, [filters, notify]);

  useEffect(() => {
    const t = setTimeout(load, 200);
    return () => clearTimeout(t);
  }, [load]);

  const saveDonor = async (body) => {
    await api.createDonor(body);
    setModal(null);
    notify('Donor registered');
    load();
    onChanged();
  };

  const saveDonation = async (donor, body) => {
    const unit = await api.recordDonation(donor.id, body);
    setModal(null);
    notify(`Unit #${unit.id} (${unit.blood_group} ${label(unit.component)}) added to stock`);
    load();
    onChanged();
  };

  const remove = async (donor) => {
    if (!confirm(`Delete donor ${donor.full_name}?`)) return;
    try {
      await api.deleteDonor(donor.id);
      notify('Donor deleted');
      load();
      onChanged();
    } catch (err) {
      notify(err.message, 'error');
    }
  };

  return (
    <section className="card">
      <header className="card-head wrap">
        <h2>Donor registry</h2>
        <div className="toolbar">
          <input type="search" placeholder="Search name or email" value={filters.q} onChange={(e) => setFilters({ ...filters, q: e.target.value })} />
          <Select value={filters.blood_group} onChange={(v) => setFilters({ ...filters, blood_group: v })} options={BLOOD_GROUPS} placeholder="All groups" />
          <select value={filters.eligible} onChange={(e) => setFilters({ ...filters, eligible: e.target.value })}>
            <option value="">Any status</option>
            <option value="true">Eligible now</option>
            <option value="false">Resting</option>
          </select>
          <button className="btn" onClick={() => setModal({ type: 'donor' })}>+ Register donor</button>
        </div>
      </header>

      {donors === null ? (
        <div className="skeleton" />
      ) : donors.length === 0 ? (
        <Empty>No donors match these filters.</Empty>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Donor</th><th>Group</th><th>City</th><th>Last donation</th><th>Status</th><th aria-label="Actions" /></tr>
            </thead>
            <tbody>
              {donors.map((d) => (
                <tr key={d.id}>
                  <td data-label="Donor"><strong>{d.full_name}</strong><small>{d.email} · {d.phone}</small></td>
                  <td data-label="Group"><GroupBadge group={d.blood_group} /></td>
                  <td data-label="City">{d.city}</td>
                  <td data-label="Last donation">{formatDate(d.last_donation_date)}</td>
                  <td data-label="Status">
                    {d.eligible ? <Pill value="ELIGIBLE" /> : <span title={`Eligible from ${d.next_eligible_on}`}><Pill value="RESTING" /> <small>until {formatDate(d.next_eligible_on)}</small></span>}
                  </td>
                  <td className="actions">
                    <button className="btn sm" disabled={!d.eligible} onClick={() => setModal({ type: 'donation', donor: d })}>Record donation</button>
                    <button className="btn sm ghost danger" onClick={() => remove(d)} aria-label={`Delete ${d.full_name}`}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modal?.type === 'donor' && <DonorForm onSave={saveDonor} onClose={() => setModal(null)} />}
      {modal?.type === 'donation' && (
        <DonationForm donor={modal.donor} onSave={(body) => saveDonation(modal.donor, body)} onClose={() => setModal(null)} />
      )}
    </section>
  );
}
