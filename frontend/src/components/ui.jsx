import { useEffect, useRef } from 'react';
import { label } from '../api.js';

export function Modal({ title, onClose, children }) {
  const ref = useRef(null);
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    ref.current?.querySelector('input, select, textarea, button')?.focus();
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-label={title} ref={ref}>
        <header className="modal-head">
          <h2>{title}</h2>
          <button className="icon-btn" onClick={onClose} aria-label="Close">×</button>
        </header>
        {children}
      </div>
    </div>
  );
}

export function GroupBadge({ group }) {
  return <span className={`group-badge ${group.endsWith('-') ? 'neg' : 'pos'}`}>{group}</span>;
}

const TONE = {
  AVAILABLE: 'ok', FULFILLED: 'ok', ELIGIBLE: 'ok',
  PENDING: 'info', ROUTINE: 'info', QUARANTINED: 'warn',
  PARTIAL: 'warn', URGENT: 'warn', RESTING: 'muted',
  CRITICAL: 'danger', EXPIRED: 'danger',
  ISSUED: 'muted', DISCARDED: 'muted', CANCELLED: 'muted',
};

export function Pill({ value }) {
  return <span className={`pill ${TONE[value] ?? 'muted'}`}>{label(value)}</span>;
}

export function Empty({ children }) {
  return <div className="empty">{children}</div>;
}

export function Field({ label: text, children, hint }) {
  return (
    <label className="field">
      <span>{text}</span>
      {children}
      {hint && <small>{hint}</small>}
    </label>
  );
}

export function Select({ value, onChange, options, placeholder, ...rest }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} {...rest}>
      {placeholder !== undefined && <option value="">{placeholder}</option>}
      {options.map((o) => (
        <option key={o} value={o}>{o.length <= 3 ? o : label(o)}</option>
      ))}
    </select>
  );
}
