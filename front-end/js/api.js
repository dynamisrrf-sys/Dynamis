const API_PREFIX = '/api/v1';
const SESSION_KEY = 'dynamis_session';

export function getSession() {
  try { return JSON.parse(localStorage.getItem(SESSION_KEY)) || null; }
  catch { return null; }
}

export function saveSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

async function refreshSession() {
  const session = getSession();
  if (!session?.refresh_token) return null;
  const response = await fetch(`${API_PREFIX}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: session.refresh_token }),
  });
  if (!response.ok) return null;
  const renewed = await response.json();
  const next = { ...session, ...renewed };
  saveSession(next);
  return next;
}

export async function api(path, options = {}, retry = true) {
  const session = getSession();
  const headers = { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...options.headers };
  if (session?.access_token) headers.Authorization = `Bearer ${session.access_token}`;

  const response = await fetch(`${API_PREFIX}${path}`, { ...options, headers });
  if (response.status === 401 && retry && session?.refresh_token) {
    const renewed = await refreshSession();
    if (renewed) return api(path, options, false);
  }

  const data = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    const message = data?.error?.message || data?.detail || 'Não foi possível concluir a operação.';
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
  }
  return data;
}

export function formToJson(form) {
  return Object.fromEntries(
    [...new FormData(form).entries()].filter(([, value]) => value !== '')
  );
}
