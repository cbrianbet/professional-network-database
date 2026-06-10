const SHELL_LINKS = [
  { href: 'dashboard.html', label: 'Dashboard' },
  { href: 'data-form.html', label: 'Register' },
  { href: 'admin.html',     label: 'Admin' },
];

async function ensureAuthenticated() {
  const token = localStorage.getItem('authToken');
  if (!token) { window.location.href = '/login'; return false; }
  try {
    const res = await fetch('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } });
    if (!res.ok) throw new Error('Unauthorized');
    return true;
  } catch {
    localStorage.removeItem('authToken');
    window.location.href = '/login';
    return false;
  }
}

function renderSidebar(activeHref) {
  return `
    <div class="sidebar-logo">
      <div class="logo-name">Professionals Databank</div>
      <button class="sidebar-close" id="sidebarClose" aria-label="Close menu">✕</button>
    </div>
    <nav class="sidebar-nav">
      ${SHELL_LINKS.map(link => `
        <a href="/${link.href.replace('.html','')}"
           class="nav-item ${link.href === activeHref ? 'active' : ''}"
           data-route="${link.href}">${link.label}</a>
      `).join('')}
    </nav>
    <div class="sidebar-footer">Professionals Databank</div>
  `;
}

function initMobileNav() {
  const hamburger = document.getElementById('hamburgerBtn');
  const overlay   = document.getElementById('sidebarOverlay');
  const sidebar   = document.querySelector('.sidebar');

  function open()  { 
    sidebar.style.removeProperty("display");
    sidebar?.classList.add('open'); overlay?.classList.add('show'); document.body.style.overflow = 'hidden'; }
  function close() { sidebar?.classList.remove('open'); overlay?.classList.remove('show'); document.body.style.overflow = ''; }

  hamburger?.addEventListener('click', open);
  document.getElementById('sidebarClose')?.addEventListener('click', close);
  overlay?.addEventListener('click', close);
  // Close on nav tap (mobile)
  sidebar?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => { if (window.innerWidth < 900) close(); }));
}

async function loadCurrentUser() {
  const token = localStorage.getItem('authToken');
  if (!token) return null;
  try {
    const res = await fetch('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } });
    if (!res.ok) throw new Error('Unauthorized');
    const data = await res.json();
    window.currentUser = data.user;
    const node = document.getElementById('authUserName');
    if (node) node.textContent = data.user.name || 'Member';
    return data.user;
  } catch {
    localStorage.removeItem('authToken');
    window.location.href = '/login';
    return null;
  }
}

function logout() {
  localStorage.removeItem('authToken');
  window.location.href = '/login';
}

async function renderProtectedPage({ title, activeHref, contentHtml, onMount, topbarHtml }) {
  document.title = `${title} — Professionals Databank`;
  const shell = document.getElementById('shared-shell');
  if (!shell) return;

  const authOk = await ensureAuthenticated();
  if (!authOk) return;

  shell.innerHTML = `
    <div class="sidebar-overlay" id="sidebarOverlay"></div>
    <div class="layout">
      <aside class="sidebar">${renderSidebar(activeHref)}</aside>
      <div class="main">
        <div class="topbar">
          <button class="topbar-hamburger" id="hamburgerBtn" aria-label="Open menu">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <line x1="3" y1="6"  x2="21" y2="6"/>
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
          <div class="page-title" id="pageTitle">${title}</div>
          ${topbarHtml || ''}
          <div class="auth-user">
            <span id="authUserName">…</span>
            <button id="logoutButton" type="button">Log out</button>
          </div>
        </div>
        <main class="page-content" id="pageContent">${contentHtml}</main>
      </div>
    </div>
  `;

  document.getElementById('logoutButton')?.addEventListener('click', logout);
  initMobileNav();
  await loadCurrentUser();
  if (typeof onMount === 'function') onMount();
}
