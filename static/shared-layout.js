/**
 * shared-layout.js — Minimal client JS for server-rendered pages.
 * Responsibilities: Sidebar toggle, AppOverlay alerts/confirms/success
 * Removed: ensureAuthenticated, localStorage, renderProtectedPage, data-fetch
 */

function openSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (sidebar) sidebar.classList.add('open');
  if (overlay) overlay.classList.add('show');
}

function closeSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (sidebar) sidebar.classList.remove('open');
  if (overlay) overlay.classList.remove('show');
}

document.addEventListener('DOMContentLoaded', () => {
  const sidebarLinks = document.querySelectorAll('.sidebar-nav a');
  sidebarLinks.forEach(link => {
    link.addEventListener('click', closeSidebar);
  });
});

const AppOverlay = {
  _show(type, title, message, actions = []) {
    const overlay = document.getElementById('appOverlay');
    const card = document.getElementById('appOverlayCard');
    const icon = document.getElementById('appOverlayIcon');
    const titleEl = document.getElementById('appOverlayTitle');
    const textEl = document.getElementById('appOverlayText');
    const actionsEl = document.getElementById('appOverlayActions');
    if (!overlay) return;
    card.className = `app-overlay-card ${type}`;
    icon.textContent = type === 'success' ? '✓' : type === 'error' ? '✕' : '?';
    titleEl.textContent = title || 'Message';
    textEl.textContent = message || '';
    actionsEl.innerHTML = '';
    actions.forEach(action => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `app-overlay-btn ${action.class || 'primary'}`;
      btn.textContent = action.label || 'OK';
      btn.onclick = action.onclick || (() => AppOverlay.hide());
      actionsEl.appendChild(btn);
    });
    overlay.classList.add('show');
  },
  success(title, message, actions = []) {
    if (!actions.length) actions = [{ label: 'OK', onclick: () => AppOverlay.hide() }];
    this._show('success', title, message, actions);
  },
  error(title, message, actions = []) {
    if (!actions.length) actions = [{ label: 'OK', onclick: () => AppOverlay.hide() }];
    this._show('error', title, message, actions);
  },
  confirm(title, message, onConfirm, onCancel = null) {
    this._show('confirm', title, message, [
      { label: 'Cancel', class: 'secondary', onclick: () => { if (onCancel) onCancel(); AppOverlay.hide(); }},
      { label: 'Confirm', class: 'danger', onclick: () => { if (onConfirm) onConfirm(); AppOverlay.hide(); }},
    ]);
  },
  hide() {
    const overlay = document.getElementById('appOverlay');
    if (overlay) overlay.classList.remove('show');
  },
};

document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('appOverlay');
  if (overlay) overlay.addEventListener('click', (e) => { if (e.target === overlay) AppOverlay.hide(); });
});
