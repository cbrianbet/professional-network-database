# Shared Protected Page Skeleton Architecture

## Overview
All protected pages (`dashboard.html`, `data-form.html`, `admin.html`) now use a centralized shared layout system that ensures:
- **Single source of truth** for sidebar, topbar, and shell styling
- **Consistent auth flow** across all protected pages
- **Simplified updates** — changes to the shell layout update all pages automatically

## File Structure

### Core Shared Files
- **`shared-layout.js`** — Core rendering and auth helpers
  - `renderProtectedPage({ title, activeHref, contentHtml, onMount })` — Main shell renderer
  - `ensureAuthenticated()` — JWT token validation
  - `loadCurrentUser()` — Fetch and display current user info
  - `logout()` — Clear auth and redirect to login
  - `renderSidebar(activeHref)` — Generate sidebar with active link highlighting
  - `SHELL_LINKS` — Navigation menu config

- **`shared-layout.css`** — Unified styling for layout
  - Sidebar layout and navigation styles
  - Topbar with user info and logout button
  - Main content area responsive grid
  - All CSS variables for consistent theming

### Page-Specific Files
Each protected page has its own HTML with page-specific styles and logic, but all render through `renderProtectedPage()`.

- **`dashboard.html`** — Main dashboard showing member statistics and management
  - Uses `renderProtectedPage()` to display shell
  - Contains page-specific JavaScript for KPIs, charts, filters, and member table
  - `initDashboardPage()` called on mount via `onMount` callback

- **`data-form.html`** — Member registration form
  - Form content in `<template id="page-body-template">`
  - `initDataFormPage()` called on mount via `onMount` callback
  - Handles member record fetch/save, skill tags, validation

- **`admin.html`** — Admin console for user management
  - User table in `<template id="page-body-template">`
  - `initAdminPage()` called on mount
  - Fetches/renders user list, handles role/status updates

## How It Works

### Page Load Flow
1. Page HTML loads with minimal markup: `<div id="shared-shell"></div>` + `<template id="page-body-template">`
2. `shared-layout.js` is loaded
3. On `DOMContentLoaded`, page calls `renderProtectedPage()`
4. `renderProtectedPage()` validates JWT token, then renders shell:
   ```
   <div class="layout">
     <aside class="sidebar">...</aside>
     <div class="main">
       <div class="topbar">...</div>
       <main class="page-content">${contentHtml}</main>
     </div>
   ```
5. Content HTML (from `<template>`) is injected into `.page-content`
6. `onMount` callback is invoked to attach page-specific event listeners

### Updating Shared Elements
To change the sidebar, topbar, or any shell styling:
1. Edit `shared-layout.css` for styles
2. Edit `shared-layout.js` for `renderSidebar()` or `renderProtectedPage()` logic
3. **All pages automatically reflect the changes** (no file duplication)

### Adding a New Protected Page
1. Create `new-page.html` with:
   - Link to `shared-layout.css` and `shared-layout.js`
   - Minimal inline styles for page-specific CSS
   - `<div id="shared-shell"></div>` container
   - `<template id="page-body-template">` with page content
   - Script that calls `renderProtectedPage({ title, activeHref: 'new-page.html', ... })`
   - `onMount` callback for event wiring

2. Add entry to `SHELL_LINKS` in `shared-layout.js`:
   ```javascript
   const SHELL_LINKS = [
     { href: 'dashboard.html', label: 'Dashboard' },
     { href: 'data-form.html', label: 'Register' },
     { href: 'admin.html', label: 'Admin' },
     { href: 'new-page.html', label: 'New Page' },  // ← Add here
   ];
   ```

## Key Benefits
✓ **DRY** — No duplicate sidebar/topbar code across pages
✓ **Consistency** — All pages share identical shell styling and nav
✓ **Maintainability** — Change shell once, apply everywhere
✓ **Scalability** — New pages reuse the skeleton immediately
✓ **Auth Centralization** — Token validation in one place
✓ **Theme Support** — CSS variables in `shared-layout.css` define all colors

## Authentication Flow
1. User logs in at `login.html`, receives JWT token
2. Token stored in `localStorage.authToken`
3. On protected page load, `ensureAuthenticated()` validates token with `/api/auth/me`
4. If valid, user info loaded and `renderProtectedPage()` displays shell
5. If invalid/expired, user redirected to `login.html`
6. Logout button clears token and redirects to `login.html`

## CSS Variable Reference (from `shared-layout.css`)
```css
--bg: #0b0f14;              /* Background */
--surface: #131920;         /* Surface level 1 */
--surface2: #1a2330;        /* Surface level 2 */
--border: rgba(255,255,255,0.08); /* Borders */
--text: #edf2f7;            /* Primary text */
--muted: #a0aec0;           /* Muted text */
--gold: #d4a843;            /* Primary accent */
--gold2: #f0c96a;           /* Secondary accent */
--radius: 14px;             /* Border radius */
--sidebar-w: 220px;         /* Sidebar width */
--topbar-h: 58px;           /* Topbar height */
--font-head: Inter, system-ui, sans-serif; /* Heading font */
--font-body: Inter, system-ui, sans-serif; /* Body font */
```

## Future Enhancements
- Move page-specific styles to external CSS files to keep HTML cleaner
- Add loading skeleton during API calls
- Implement breadcrumb navigation
- Add user role indicators in sidebar
- Extend admin tools (user creation, deletion, etc.)