const defaultApiBase = import.meta.env.PROD
  ? 'https://oasis-technologies-api.onrender.com/api/v1'
  : 'http://localhost:8000/api/v1';
const configuredApiBase = (import.meta.env.VITE_API_BASE_URL || defaultApiBase).replace(/\/+$/, '');
// Accept either the API host or a host that already includes /api/v1.
// This prevents production environment-variable mistakes from dropping the API prefix.
export const API_BASE = /\/api\/v1$/i.test(configuredApiBase)
  ? configuredApiBase
  : `${configuredApiBase}/api/v1`;

export async function apiRequest(path, options = {}) {
 const normalizedPath = path.startsWith('/') ? path : `/${path}`;
 const response = await fetch(API_BASE + normalizedPath, {
   ...options,
   headers: {'Content-Type':'application/json', ...(options.headers || {})}
 });
 const data = await response.json().catch(() => ({}));
 if (!response.ok) throw new Error(data.detail || 'Something went wrong. Please try again.');
 return data;
}
