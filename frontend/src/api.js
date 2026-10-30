const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');
export async function apiRequest(path, options = {}) {
 const response = await fetch(API_BASE + path, {...options, headers: {'Content-Type':'application/json', ...(options.headers || {})}});
 const data = await response.json().catch(() => ({}));
 if (!response.ok) throw new Error(data.detail || 'Something went wrong. Please try again.');
 return data;
}
