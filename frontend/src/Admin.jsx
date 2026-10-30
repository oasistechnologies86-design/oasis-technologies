import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiRequest } from './api.js';

const TOKEN_KEY = 'oasis_admin_token';
const API_ROOT = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');

async function adminRequest(path, token, options = {}) {
  const response = await fetch(API_ROOT + path, {
    ...options,
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}`, ...(options.headers || {}) },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || 'Request failed. Please try again.');
  return data;
}

function AdminFrame({ children, onLogout }) {
  return <div className="admin-shell">
    <header className="admin-top"><Link to="/" className="brand"><span className="brand-mark">O</span> oasis <small>technologies</small></Link><button className="admin-logout" onClick={onLogout}>Sign out</button></header>
    <main className="admin-main">{children}</main>
    <footer className="admin-foot">Oasis Technologies · Internal team area</footer>
  </div>;
}

export default function Admin({ initialPage = 'login' }) {
  const navigate = useNavigate();
  const [token, setToken] = useState(() => sessionStorage.getItem(TOKEN_KEY) || '');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [items, setItems] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const logout = useCallback(() => {
    sessionStorage.removeItem(TOKEN_KEY);
    setToken('');
    setItems([]);
    setPassword('');
    setError('');
    navigate('/team/login', { replace: true });
  }, [navigate]);

  const loadItems = useCallback(async (currentToken) => {
    setBusy(true);
    setError('');
    try {
      const result = await adminRequest('/admin/enquiries', currentToken);
      setItems(result.items || []);
    } catch (err) {
      if (/session is invalid|expired|sign in/i.test(err.message)) {
        logout();
        return;
      }
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }, [logout]);

  useEffect(() => {
    if (initialPage === 'enquiries' && !token) navigate('/team/login', { replace: true });
    else if (initialPage === 'enquiries' && token) loadItems(token);
  }, [initialPage, token, loadItems, navigate]);

  async function submitLogin(event) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      const result = await apiRequest('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
      sessionStorage.setItem(TOKEN_KEY, result.access_token);
      setToken(result.access_token);
      setPassword('');
      navigate('/team/enquiries', { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function updateStatus(id, status) {
    if (!token) return;
    setNotice('');
    setError('');
    try {
      await adminRequest(`/admin/enquiries/${id}`, token, { method: 'PATCH', body: JSON.stringify({ status }) });
      setItems(current => current.map(item => item.id === id ? { ...item, status } : item));
      setNotice('Enquiry status updated.');
    } catch (err) {
      setError(err.message);
    }
  }

  if (initialPage === 'login' && token) {
    return <AdminFrame onLogout={logout}><section className="admin-card"><p>You're already signed in.</p><button className="button primary" onClick={() => navigate('/team/enquiries')}>Open enquiries →</button></section></AdminFrame>;
  }

  if (initialPage === 'login') {
    return <AdminFrame onLogout={() => {}}><section className="admin-card admin-login-card">
      <div className="eyebrow dark">RESTRICTED ACCESS</div><h1>Team <span>sign in.</span></h1><p>Authorized Oasis team members only.</p>
      <form className="form admin-form" onSubmit={submitLogin}>
        <label>Admin email<input required type="email" autoComplete="username" maxLength="254" value={email} onChange={e => setEmail(e.target.value)} /></label>
        <label>Password<input required type="password" autoComplete="current-password" maxLength="1024" value={password} onChange={e => setPassword(e.target.value)} /></label>
        {error && <p className="error" role="alert">{error}</p>}
        <button className="button primary submit" disabled={busy}>{busy ? 'Signing in…' : 'Sign in securely ↗'}</button>
      </form>
      <Link className="admin-back" to="/">← Back to website</Link>
    </section></AdminFrame>;
  }

  return <AdminFrame onLogout={logout}><div className="admin-heading"><div><div className="eyebrow dark">TEAM WORKSPACE</div><h1>Customer <span>enquiries.</span></h1><p>Review messages submitted through the website and keep their status up to date.</p></div><button className="button quiet" onClick={() => loadItems(token)} disabled={busy}>↻ Refresh</button></div>
    {error && <p className="error" role="alert">{error}</p>}{notice && <p className="success" role="status">{notice}</p>}
    <div className="admin-summary"><b>{items.length}</b><span>latest enquiries · maximum 250 shown</span></div>
    {busy && items.length === 0 ? <p>Loading enquiries…</p> : items.length === 0 ? <section className="admin-card"><h2>No enquiries yet</h2><p>New contact form submissions will appear here.</p></section> : <div className="enquiry-list">{items.map(item => <article className="enquiry-card" key={item.id}>
      <div className="enquiry-head"><div><h2>{item.name}</h2><a href={`mailto:${item.email}`}>{item.email}</a>{item.company && <p>{item.company}</p>}</div><label className="status-label">Status<select value={item.status} onChange={e => updateStatus(item.id, e.target.value)}><option value="new">New</option><option value="in_progress">In progress</option><option value="resolved">Resolved</option></select></label></div>
      <div className="enquiry-meta"><span>{item.service}</span><time dateTime={item.created_at}>{new Date(item.created_at).toLocaleString()}</time></div>
      <p className="enquiry-message">{item.message}</p>
    </article>)}</div>}
  </AdminFrame>;
}
