const SHELL_LINKS = [
  { href: 'dashboard.html', label: 'Dashboard' },
  { href: 'data-form.html', label: 'Register' },
  { href: 'admin.html', label: 'Admin' },
];

async function ensureAuthenticated() {
  const token = localStorage.getItem('authToken');
  if (!token) {
    window.location.href = 'login.html';
    return false;
  }
  try {
    const res = await fetch('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Unauthorized');
    return true;
  } catch (err) {
    localStorage.removeItem('authToken');
    window.location.href = 'login.html';
    return false;
  }
}

function renderSidebar(activeHref) {
  return `
    <div class="sidebar-logo">
      <div class="logo-name">Professionals Databank</div>
    </div>
    <nav class="sidebar-nav">
      ${SHELL_LINKS.map(link => `
        <a href="${link.href}" class="nav-item ${link.href === activeHref ? 'active' : ''}" data-route="${link.href}">${link.label}</a>
      `).join('')}
    </nav>
    <div class="sidebar-footer">Shared protected shell for dashboard, registration, and admin.</div>
  `;
}

async function loadCurrentUser() {
  const token = localStorage.getItem('authToken');
  if (!token) return null;
  try {
    const res = await fetch('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Unauthorized');
    const data = await res.json();
    const nameNode = document.getElementById('authUserName');
    if (nameNode) nameNode.textContent = data.user.name || 'Member';
    return data.user;
  } catch (err) {
    localStorage.removeItem('authToken');
    window.location.href = 'login.html';
    return null;
  }
}

function logout() {
  localStorage.removeItem('authToken');
  window.location.href = 'login.html';
}

async function renderProtectedPage({ title, activeHref, contentHtml, onMount, topbarHtml }) {
  document.title = `${title} — Professionals Databank`;
  const shell = document.getElementById('shared-shell');
  if (!shell) {
    console.warn('Shared shell container not found');
    return;
  }

  const authOk = await ensureAuthenticated();
  if (!authOk) return;

  shell.innerHTML = `
    <div class="layout">
      <aside class="sidebar">
        ${renderSidebar(activeHref)}
      </aside>
      <div class="main">
        <div class="topbar">
          <div class="page-title">${title}</div>
          ${topbarHtml || ''}
          <div class="auth-user">
            <span id="authUserName">Signed in</span>
            <button id="logoutButton" type="button">Log out</button>
          </div>
        </div>
        <main class="page-content" id="pageContent">${contentHtml}</main>
      </div>
    </div>
  `;

  const logoutButton = document.getElementById('logoutButton');
  if (logoutButton) {
    logoutButton.addEventListener('click', logout);
  }

  await loadCurrentUser();
  if (typeof onMount === 'function') {
    onMount();
  }
}
