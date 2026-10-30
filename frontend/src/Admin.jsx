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
  const [siteSettings, setSiteSettings] = useState({company_name:'Oasis Technologies',contact_email:'oasistechnologies86@gmail.com',phone_primary:'0246470941',phone_secondary:'0201491597',tagline:'Thoughtful technology. Real-world impact.',hero_title:'Build what is next.',hero_accent:'Make it matter.',hero_description:'We build useful digital products and deliver dependable IT services that help ambitious businesses move forward.'});
  const [settingsBusy, setSettingsBusy] = useState(false);

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
      const savedSettings = await adminRequest('/admin/site-settings', currentToken);
      setSiteSettings(current => ({...current, ...savedSettings}));
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


  async function saveSiteSettings(event) {
    event.preventDefault();
    if (!token) return;
    setSettingsBusy(true);
    setError('');
    setNotice('');
    try {
      const saved = await adminRequest('/admin/site-settings', token, { method: 'PUT', body: JSON.stringify(siteSettings) });
      setSiteSettings(current => ({...current, ...saved}));
      setNotice('Website settings saved. Public pages now use the updated details.');
    } catch (err) {
      setError(err.message);
    } finally {
      setSettingsBusy(false);
    }
  }

  function changeSiteSetting(event) {
    setSiteSettings(current => ({...current, [event.target.name]: event.target.value}));
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
    <section className="admin-card site-settings-card">
      <div className="eyebrow dark">WEBSITE CONTENT</div>
      <h2>Update public details.</h2>
      <p>Changes saved here are shared by the contact page, homepage and footer. Phone numbers are clickable for visitors.</p>
      <form className="form admin-form settings-form" onSubmit={saveSiteSettings}>
        <div className="form-row">
          <label>Company name<input name="company_name" required maxLength="120" value={siteSettings.company_name} onChange={changeSiteSetting}/></label>
          <label>Public contact email<input type="email" name="contact_email" required maxLength="254" value={siteSettings.contact_email} onChange={changeSiteSetting}/></label>
        </div>
        <div className="form-row">
          <label>Primary phone<input type="tel" name="phone_primary" required maxLength="40" value={siteSettings.phone_primary} onChange={changeSiteSetting}/></label>
          <label>Second phone<input type="tel" name="phone_secondary" required maxLength="40" value={siteSettings.phone_secondary} onChange={changeSiteSetting}/></label>
        </div>
        <label>Tagline (footer)<input name="tagline" required maxLength="240" value={siteSettings.tagline} onChange={changeSiteSetting}/></label>
        <div className="form-row">
          <label>Homepage heading<input name="hero_title" required maxLength="120" value={siteSettings.hero_title} onChange={changeSiteSetting}/></label>
          <label>Homepage highlighted heading<input name="hero_accent" required maxLength="120" value={siteSettings.hero_accent} onChange={changeSiteSetting}/></label>
        </div>
        <label>Homepage introduction<textarea name="hero_description" required minLength="10" maxLength="1000" rows="3" value={siteSettings.hero_description} onChange={changeSiteSetting}/></label>
        <button className="button primary" disabled={settingsBusy}>{settingsBusy ? 'Saving settings…' : 'Save website settings ↗'}</button>
      </form>
    </section>
    <div className="admin-summary"><b>{items.length}</b><span>latest enquiries · maximum 250 shown</span></div>
    {busy && items.length === 0 ? <p>Loading enquiries…</p> : items.length === 0 ? <section className="admin-card"><h2>No enquiries yet</h2><p>New contact form submissions will appear here.</p></section> : <div className="enquiry-list">{items.map(item => <article className="enquiry-card" key={item.id}>
      <div className="enquiry-head"><div><h2>{item.name}</h2><a href={`mailto:${item.email}`}>{item.email}</a>{item.company && <p>{item.company}</p>}</div><label className="status-label">Status<select value={item.status} onChange={e => updateStatus(item.id, e.target.value)}><option value="new">New</option><option value="in_progress">In progress</option><option value="resolved">Resolved</option></select></label></div>
      <div className="enquiry-meta"><span>{item.service}</span><time dateTime={item.created_at}>{new Date(item.created_at).toLocaleString()}</time></div>
      <p className="enquiry-message">{item.message}</p>
    </article>)}</div>}
  </AdminFrame>;
}
