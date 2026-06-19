# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

1. **Prerequisites**: Python 3.14+, pip, PostgreSQL (or Supabase)
2. **Environment**: Copy `.env.example` to `.env` and fill in the required variables (DJANGO_SECRET_KEY, DATABASE_URL, etc.)
3. **Dependencies**: Install with `pip install -r requirements.txt`
4. **Database**: Run migrations with `python manage.py migrate`
5. **Create Superuser** (optional): `python manage.py createsuperuser`
6. **Static Files**: Collect static files for production with `python manage.py collectstatic`

## Common Commands

- **Start Development Server**: `python manage.py runserver`
- **Run Migrations**: `python manage.py migrate`
- **Create Migration**: `python manage.py makemigrations`
- **Run Tests**: `python manage.py test` (Note: No tests are currently configured; this command will run if tests are added)
- **Shell**: `python manage.py shell` for Django shell
- **Collect Static**: `python manage.py collectstatic`
- **Check**: `python manage.py check` for common errors
- **Lint**: No linter configured; consider adding flake8 or pylint

## Code Architecture

### Backend (Django)

- **Settings**: `settings.py` - Django configuration, including database, JWT auth, CORS, static files
- **URLs**: 
  - Root `urls.py` - maps frontend pages and includes API URLs
  - `api/urls.py` - defines REST API endpoints
- **Apps**: 
  - `api` - contains models, views, serializers for the application
- **Models** (`api/models.py`):
  - `User`: Custom user model (email-based, role/status fields)
  - `Member`: Member records linked to a user
  - `Profile`: Professional profiles (similar to LinkedIn) linked to a user
- **Views** (`api/views.py`): 
  - Authentication: login, signup, me (current user)
  - CRUD operations for members, profiles, admin endpoints
  - Export endpoints for CSV
- **Serializers** (`api/serializers.py`): DRF serializers for models
- **Authentication**: JWT via `djangorestframework-simplejwt`; token stored in `localStorage` on frontend
- **Permissions**: Custom permissions in `api/permissions.py` (e.g., IsAdminUser)
- **CORS**: Configured to allow all origins (for development)

### Frontend (Shared Layout System)

All protected pages (`dashboard.html`, `data-form.html`, `admin.html`) use a centralized layout system:

- **Shared Files** (`static/`):
  - `shared-layout.js`: Core rendering and auth helpers
    - `renderProtectedPage({ title, activeHref, contentHtml, onMount })` - Main shell renderer
    - `ensureAuthenticated()` - JWT token validation
    - `loadCurrentUser()` - Fetch and display current user info
    - `logout()` - Clear auth and redirect to login
    - `renderSidebar(activeHref)` - Generate sidebar with active link highlighting
    - `SHELL_LINKS` - Navigation menu config
  - `shared-layout.css`: Unified styling for layout (sidebar, topbar, main content)
    - Uses CSS variables for theming (see `shared-layout.css` for values)
- **Page-Specific Files** (`templates/`):
  - Each page has minimal markup: `<div id="shared-shell"></div>` + `<template id="page-body-template">`
  - On `DOMContentLoaded`, calls `renderProtectedPage()` with page-specific config
  - Content HTML (from template) is injected into `.page-content`
  - `onMount` callback attaches page-specific event listeners
- **Authentication Flow**:
  1. User logs in at `login.html`, receives JWT token
  2. Token stored in `localStorage.authToken`
  3. On protected page load, `ensureAuthenticated()` validates token with `/api/auth/me`
  4. If valid, user info loaded and shell rendered
  5. If invalid/expired, user redirected to `login.html`
  6. Logout button clears token and redirects to `login.html`

## Key Benefits of Shared Layout

- **DRY**: No duplicate sidebar/topbar code across pages
- **Consistency**: All pages share identical shell styling and navigation
- **Maintainability**: Change shell once, apply everywhere
- **Scalability**: New pages reuse the skeleton immediately
- **Auth Centralization**: Token validation in one place
- **Theme Support**: CSS variables in `shared-layout.css` define all colors

## Adding a New Protected Page

1. Create `new-page.html` in `templates/` with:
   - Link to `shared-layout.css` and `shared-layout.js`
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
     { href: 'new-page.html', label: 'New Page' },
   ];
   ```

## API Endpoints

See `api/urls.py` for full list. Key endpoints:

- **Auth**: 
  - POST `/api/auth/signup` - user registration
  - POST `/api/auth/login` - user login
  - GET `/api/auth/me` - current user info
- **Members**:
  - GET/POST `/api/members` - list/create members
  - GET/PATCH/DELETE `/api/members/<int:member_id>` - member detail
- **Profiles**:
  - GET/POST `/api/profiles` - list/create profiles
  - GET/PATCH `/api/profiles/<int:profile_id>` - profile detail
- **Admin**:
  - GET/POST `/api/admin/users` - list/create users (admin only)
  - PATCH `/api/admin/users/<int:user_id>` - update user (admin only)
  - GET `/api/admin/members` - create member (admin only)
  - GET `/api/admin/export/members` - export members CSV
  - GET `/api/admin/export/users` - export users CSV

## Database

- Uses PostgreSQL (configured via `DATABASE_URL` in `.env`)
- Tables: `users`, `members`, `profiles` (matches existing Node project schema)
- Migrations are in `api/migrations/`

## Environment Variables

- `DJANGO_SECRET_KEY`: Django secret key
- `DEBUG`: Set to `True` for development, `False` for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: PostgreSQL connection string (or individual DB_* variables)
- `JWT_SECRET`: Secret for JWT signing (defaults to SECRET_KEY)
- `ADMIN_EMAIL`: Email for admin user (for seeding)
- `ADMIN_PASSWORD`: Password for admin user (for seeding)

## Notes

- The frontend is served directly by Django via `TemplateView` (see root `urls.py`)
- Static files are served by WhiteNoise in production
- No build step required for frontend; HTML/CSS/JS are served as static files
- For production, set `DEBUG=False` and ensure `ALLOWED_HOSTS` is set appropriately