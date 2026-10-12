// Thin wrapper around fetch. All calls are relative (/api/...) so the same build works behind
// the Vite dev proxy, the Nginx container and the Kubernetes Ingress.

function describeError(body, status) {
  if (!body) return `Request failed (${status})`;
  if (typeof body.detail === 'string') return body.detail;
  if (Array.isArray(body.detail)) {
    return body.detail.map((d) => `${d.loc?.slice(-1)[0] ?? 'field'}: ${d.msg}`).join('; ');
  }
  return `Request failed (${status})`;
}

async function request(path, { method = 'GET', body, params } = {}) {
  const query = params
    ? '?' + new URLSearchParams(Object.entries(params).filter(([, v]) => v !== '' && v != null)).toString()
    : '';
  const response = await fetch(`/api${path}${query}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok) throw new Error(describeError(data, response.status));
  return data;
}

export const api = {
  meta: () => request('/meta'),
  summary: () => request('/inventory/summary'),
  compatibility: (blood_group, component) => request('/compatibility', { params: { blood_group, component } }),

  donors: (params) => request('/donors', { params }),
  createDonor: (body) => request('/donors', { method: 'POST', body }),
  updateDonor: (id, body) => request(`/donors/${id}`, { method: 'PUT', body }),
  deleteDonor: (id) => request(`/donors/${id}`, { method: 'DELETE' }),
  recordDonation: (id, body) => request(`/donors/${id}/donations`, { method: 'POST', body }),

  units: (params) => request('/units', { params }),
  updateUnit: (id, status) => request(`/units/${id}`, { method: 'PUT', body: { status } }),
  expireSweep: () => request('/units/expire-sweep', { method: 'POST' }),

  requests: (params) => request('/requests', { params }),
  createRequest: (body) => request('/requests', { method: 'POST', body }),
  updateRequest: (id, body) => request(`/requests/${id}`, { method: 'PUT', body }),
  deleteRequest: (id) => request(`/requests/${id}`, { method: 'DELETE' }),
  fulfil: (id) => request(`/requests/${id}/fulfil`, { method: 'POST' }),
};

export const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
export const COMPONENTS = ['WHOLE_BLOOD', 'RED_CELLS', 'PLASMA', 'PLATELETS'];
export const URGENCIES = ['ROUTINE', 'URGENT', 'CRITICAL'];

export const label = (value) =>
  value ? value.toLowerCase().replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase()) : '';

export function daysUntil(isoDate) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.round((new Date(`${isoDate}T00:00:00`) - today) / 86_400_000);
}

export const formatDate = (iso) =>
  iso ? new Date(iso.length === 10 ? `${iso}T00:00:00` : iso).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' }) : '—';
