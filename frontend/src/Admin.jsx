import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiRequest, API_BASE } from './api.js';

const TOKEN_KEY = 'oasis_admin_token';
async function adminRequest(path, token, options = {}) {
  const response = await fetch(API_BASE + (path.startsWith('/') ? path : `/${path}`), {
    ...options,
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}`, ...(options.headers || {}) },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || 'Request failed. Please try again.');
  return data;
}

function AdminFrame({ children, onLogout }) {
  return <div className="admin-shell">
    <header className="admin-top"><Link to="/" className="brand"><span className="brand-mark">O</span> oasis <small>technologies</small></Link><button className="admin-logout" onClick={() => onLogout && setConfirmLogout(true)}>Sign out</button>{confirmLogout && <div className="confirm-backdrop" role="dialog" aria-modal="true" aria-labelledby="logout-title"><section className="confirm-card"><div className="eyebrow dark">LEAVE WORKSPACE</div><h2 id="logout-title">Sign out of Oasis?</h2><p>You will need to sign in again to view customer enquiries and website settings.</p><div className="confirm-actions"><button type="button" className="button call-secondary" onClick={() => setConfirmLogout(false)}>Stay signed in</button><button type="button" className="button primary" onClick={() => { setConfirmLogout(false); onLogout?.(); }}>Yes, sign out</button></div></section></div></header>
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
  const [confirmLogout, setConfirmLogout] = useState(false);
  const [serviceItems, setServiceItems] = useState([]);
  const [serviceDraft, setServiceDraft] = useState({title:'',description:'',active:true,sort_order:0});
  const [editingServiceId, setEditingServiceId] = useState(null);
  const [serviceBusy, setServiceBusy] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [serviceFilter, setServiceFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');

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
      const servicesResult = await adminRequest('/admin/services', currentToken);\n      setServiceItems(servicesResult.items || []);\n      const savedSettings = await adminRequest('/admin/site-settings', currentToken);
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

  async function saveService(event) {
    event.preventDefault();
    if (!token) return;
    setServiceBusy(true); setError(''); setNotice('');
    try {
      const payload = {...serviceDraft, sort_order:Number(serviceDraft.sort_order)||0};
      if (editingServiceId) await adminRequest('/admin/services/' + editingServiceId, token, {method:'PUT',body:JSON.stringify(payload)});
      else await adminRequest('/admin/services', token, {method:'POST',body:JSON.stringify(payload)});
      const refreshed = await adminRequest('/admin/services', token);
      setServiceItems(refreshed.items || []);
      setServiceDraft({title:'',description:'',active:true,sort_order:0});
      const wasEditing = Boolean(editingServiceId);
      setEditingServiceId(null);
      setNotice(wasEditing ? 'Service updated.' : 'Service created and saved.');
    } catch (err) { setError(err.message); }
    finally { setServiceBusy(false); }
  }

  async function archiveService(service) {
    if (!window.confirm('Remove "' + service.title + '" from the public services page? Past enquiries will be kept.')) return;
    try {
      await adminRequest('/admin/services/' + service.id, token, {method:'DELETE'});
      setServiceItems(current => current.map(item => item.id === service.id ? {...item,active:false} : item));
      setNotice('Service removed from the public website. Past enquiries are preserved.');
    } catch (err) { setError(err.message); }
  }

  const filteredItems = items.filter(item => {
    const q = searchText.trim().toLowerCase();
    const matchesSearch = !q || [item.name,item.email,item.phone,item.company,item.service,item.message].some(value => String(value||'').toLowerCase().includes(q));
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
    const matchesService = serviceFilter === 'all' || item.service === serviceFilter;
    const age = Date.now() - new Date(item.created_at).getTime();
    const matchesDate = dateFilter === 'all' || (dateFilter === 'today' && new Date(item.created_at).toDateString() === new Date().toDateString()) || (dateFilter === '7days' && age < 7*86400000) || (dateFilter === '30days' && age < 30*86400000);
    return matchesSearch && matchesStatus && matchesService && matchesDate;
  });

  if (initialPage === 'login' && token) {
    return <AdminFrame onLogout={logout}><section className="admin-card"><p>You're already signed in.</p><button className="button primary" onClick={() => navigate('/team/enquiries')}>Open enquiries →</button></section></AdminFrame>;
  }

  if (initialPage === 'login') {
    return <AdminFrame onLogout={() => {}}><div className="admin-login-layout">
      <aside className="admin-login-aside">
        <div className="admin-login-monogram">O<span>.</span></div>
        <div className="eyebrow">OASIS TECHNOLOGIES / TEAM</div>
        <h1>Good work<br/>starts with <span>clarity.</span></h1>
        <p>A focused space to look after customer enquiries and keep the details of our website up to date.</p>
        <div className="admin-login-rule"><span></span> INTERNAL WORKSPACE · AUTHORISED TEAM ONLY</div>
      </aside>
      <section className="admin-card admin-login-card">
        <div className="admin-login-lock" aria-hidden="true">↗</div>
        <div className="eyebrow dark">SECURE TEAM ACCESS</div><h2>Welcome <span>back.</span></h2><p>Sign in with your authorised administrator account.</p>
        <form className="form admin-form" onSubmit={submitLogin}>
          <label>Admin email<input required type="email" autoComplete="username" maxLength="254" value={email} onChange={e => setEmail(e.target.value)} placeholder="admin@yourcompany.com" /></label>
          <label>Password<input required type="password" autoComplete="current-password" maxLength="1024" value={password} onChange={e => setPassword(e.target.value)} placeholder="Enter your password" /></label>
          {error && <p className="error" role="alert">{error}</p>}
          <button className="button primary submit" disabled={busy}>{busy ? 'Signing in securely…' : 'Sign in to workspace →'}</button>
        </form>
        <div className="admin-login-security"><span aria-hidden="true">◈</span> Private access for authorised Oasis team members.</div>
        <Link className="admin-back" to="/">← Return to public website</Link>
      </section>
    </div></AdminFrame>;
  }

  return <AdminFrame onLogout={logout}><div className="admin-heading"><div><div className="eyebrow dark">OASIS / OPERATIONS</div><h1>Your team <span>workspace.</span></h1><p>Good service starts with a thoughtful response. Review new enquiries, follow up with customers, and keep website details current.</p></div><button className="button quiet admin-refresh" onClick={() => loadItems(token)} disabled={busy}>↻ {busy ? 'Refreshing…' : 'Refresh inbox'}</button></div>
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
    <section className="admin-card service-manager">
      <div className="eyebrow dark">PUBLIC SERVICES</div><h2>Manage your services.</h2><p>Create, edit, reorder, or remove services. Active services appear on the public website and in the enquiry form.</p>
      <form className="form admin-form service-editor" onSubmit={saveService}>
        <div className="form-row"><label>Service name *<input required minLength="2" maxLength="120" value={serviceDraft.title} onChange={e=>setServiceDraft({...serviceDraft,title:e.target.value})} placeholder="e.g. Cybersecurity review"/></label><label>Display order<input type="number" min="0" max="10000" value={serviceDraft.sort_order} onChange={e=>setServiceDraft({...serviceDraft,sort_order:e.target.value})}/></label></div>
        <label>Description *<textarea required minLength="10" maxLength="2000" rows="3" value={serviceDraft.description} onChange={e=>setServiceDraft({...serviceDraft,description:e.target.value})} placeholder="Explain the service clearly to customers"/></label>
        <label className="service-active-toggle"><input type="checkbox" checked={serviceDraft.active} onChange={e=>setServiceDraft({...serviceDraft,active:e.target.checked})}/> Show this service on the public website</label>
        <div className="service-editor-actions"><button className="button primary" disabled={serviceBusy}>{serviceBusy?'Saving…':editingServiceId?'Save service changes':'Add service ↗'}</button>{editingServiceId&&<button type="button" className="button call-secondary" onClick={()=>{setEditingServiceId(null);setServiceDraft({title:'',description:'',active:true,sort_order:0})}}>Cancel edit</button>}</div>
      </form>
      <div className="managed-services">{serviceItems.map(service=><article className={!service.active?'managed-service archived':'managed-service'} key={service.id}><div><span className="managed-service-state">{service.active?'LIVE ON WEBSITE':'HIDDEN'}</span><h3>{service.title}</h3><p>{service.description}</p><small>Display order: {service.sort_order}</small></div><div className="managed-service-actions"><button type="button" className="button call-secondary" onClick={()=>{setEditingServiceId(service.id);setServiceDraft({title:service.title,description:service.description,active:service.active,sort_order:service.sort_order})}}>Edit</button>{service.active&&<button type="button" className="admin-archive" onClick={()=>archiveService(service)}>Remove</button>}</div></article>)}</div>
    </section>
    <div className="admin-summary"><b>{filteredItems.length}</b><span>matching enquiries · {items.length} loaded</span><small>Search customer details or message text, then narrow by status, service, or date.</small></div>
    <section className="admin-card enquiry-filters"><div className="eyebrow dark">FIND AN ENQUIRY</div><div className="enquiry-filter-grid">
      <label>Search<input type="search" value={searchText} onChange={e=>setSearchText(e.target.value)} placeholder="Name, email, phone, company, message…"/></label>
      <label>Status<select value={statusFilter} onChange={e=>setStatusFilter(e.target.value)}><option value="all">All statuses</option><option value="new">New</option><option value="in_progress">In progress</option><option value="resolved">Resolved</option></select></label>
      <label>Service<select value={serviceFilter} onChange={e=>setServiceFilter(e.target.value)}><option value="all">All services</option>{Array.from(new Set(items.map(item=>item.service))).map(service=><option key={service} value={service}>{service}</option>)}</select></label>
      <label>Date received<select value={dateFilter} onChange={e=>setDateFilter(e.target.value)}><option value="all">Any time</option><option value="today">Today</option><option value="7days">Last 7 days</option><option value="30days">Last 30 days</option></select></label>
      <button type="button" className="button call-secondary clear-filters" onClick={()=>{setSearchText('');setStatusFilter('all');setServiceFilter('all');setDateFilter('all')}}>Clear filters</button>
    </div></section>
    {busy && items.length === 0 ? <p>Loading enquiries…</p> : items.length === 0 ? <section className="admin-card"><h2>No enquiries yet</h2><p>New contact form submissions will appear here.</p></section> : filteredItems.length === 0 ? <section className="admin-card"><h2>No matching enquiries</h2><p>Try changing the search or clearing the filters.</p></section> : <div className="enquiry-list">{filteredItems.map(item => <article className="enquiry-card" key={item.id}>
      <div className="enquiry-head"><div><h2>{item.name}</h2><a href={"mailto:"+item.email}>{item.email}</a><a href={"tel:"+(item.phone||"")} className="enquiry-phone">{item.phone||"No phone supplied on older enquiry"}</a>{item.company && <p>{item.company}</p>}</div><label className="status-label">Status<select value={item.status} onChange={e => updateStatus(item.id, e.target.value)}><option value="new">New</option><option value="in_progress">In progress</option><option value="resolved">Resolved</option></select></label></div>
      <div className="enquiry-meta"><span>{item.service}</span><time dateTime={item.created_at}>{new Date(item.created_at).toLocaleString()}</time></div>
      <p className="enquiry-message">{item.message}</p>
    </article>)}</div>}
  </AdminFrame>;
}
