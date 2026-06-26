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
- **Run Tests (pytest — preferred)**: `pytest` (uses SQLite via `test_settings.py`, discovers `api/tests/`)
- **Run specific test file**: `pytest api/tests/test_bulk_upload.py -v`
- **Run tests in parallel**: `pytest -n auto`
- **Run with coverage**: `coverage run -m pytest && coverage report -m`
- **Run Tests (Django runner, legacy)**: `python manage.py test` (still works for backward compat)
- **Shell**: `python manage.py shell` for Django shell
- **Collect Static**: `python manage.py collectstatic`
- **Check**: `python manage.py check` for common errors
- **Lint**: No linter configured; consider adding flake8 or pylint

## Test-Driven Development

The project uses **pytest + pytest-django** as the primary test framework, with
`test_settings.py` providing a fast SQLite in-memory database and migration-free
setup.

### Test layout

```
pytest.ini                         # config: DJANGO_SETTINGS_MODULE=test_settings
conftest.py                        # project-level fixtures (admin_user, regular_user, make_user, make_member)
api/tests/
├── __init__.py
├── conftest.py                    # re-exports conftest.py fixtures
├── helpers.py                     # auth_client(), admin_client(), make_csv() utilities
├── test_models.py                 # existing Django TestCase tests
├── test_serializers.py            # existing Django TestCase tests
├── test_views.py                  # existing Django TestCase tests
├── test_file_resources.py         # existing Django TestCase tests (some pre-existing failures)
└── test_bulk_upload.py            # new pytest-native tests for bulk upload + CSV template
```

### Fixtures and helpers

```python
# conftest.py — available in all test files
def test_creates_member(admin_user, make_member):
    make_member(national_id='UNIQUE123')  # auto-increments unique IDs

# helpers.py — for API tests
from api.tests.helpers import admin_client, make_csv
client = admin_client(admin_user)
csv_file, _ = make_csv([{'name': 'Test', 'national_id': 'X1', ...}])
res = client.post(reverse('api:admin-members-bulk-upload'), {'file': csv_file}, format='multipart')
```

### Key TDD conventions

- Use **pytest-style** (plain `assert`, `db` fixture) for new tests — not `TestCase.setUp`
- All URL `reverse()` calls use namespaced names: `reverse('api:admin-members-bulk-upload')`
  — `app_name = 'api'` is set in `api/urls.py`
- Tests run against SQLite in-memory — no Postgres required
- For file upload tests, `make_csv()` builds a `BytesIO` with `.name = 'members.csv'`
  set (the view checks `uploaded_file.name.lower().endswith('.csv')`)
- Placeholder users created by bulk upload have emails starting with `bulk_` — assert
  with `User.objects.filter(email__startswith='bulk_').exists()`
- Existing `manage.py test` command still works (backward compat with Django TestCase tests)

### Running tests during development

```bash
# Fast iteration — run only the file you're working on
pytest api/tests/test_bulk_upload.py -v --tb=short

# Full suite before commit
pytest -q

# Parallel + coverage
coverage run -m pytest -n auto -q && coverage report -m
```

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
  - `Member`: Member records linked to a user (required ForeignKey)
  - `Profile`: Professional profiles (similar to LinkedIn) linked to a user
  - `FileResource`: Uploaded files (PDF/image) with thumbnail support
  - `JobAdvert`: Job postings with optional file (FK to FileResource) and optional link
- **Views** (`api/views.py`): 
  - Authentication: login, signup, me (current user)
  - CRUD operations for members, profiles, admin endpoints
  - Job Adverts: public list (with deadline/30-day filter), admin create/delete
  - Bulk Member Upload: CSV upload with validation report, auto-creates placeholder users
  - Export endpoints for CSV (members, users) — password-protected zip via `_encrypt_and_stream_csv`
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

## Alert & Notification System

All user-facing alerts use a centralized `AppOverlay` system — **never use `alert()` or
`confirm()` directly**. The overlay is already included in `shared-layout.js` and
`shared-layout.css`, so it's available on every API

```javascript
// Success modal (green checkmark)
AppOverlay.success('Export Ready', 'Your file is ready.', 'Download');

// Error modal (red X)
AppOverlay.error('Delete Failed', err.message);

// Confirmation modal (returns Promise<boolean>)
const confirmed = await AppOverlay.confirm('Delete Member?', 'This cannot be undone.');
if (!confirmed) return;
```

### Usage rules

- **Protected pages** (dashboard, admin, data-form, jobs): `AppOverlay` is auto-loaded
  via `shared-layout.js`. Use it directly.
- **Standalone pages** (login.html, signup.html): include the inline `AppOverlay` CSS + JS
  block directly in the template (copy from data-form.html's pre-2026-06-26 version or
  extract from shared-layout.js). The global `window.AppOverlay` object is the same API.
- **Confirm for destructive actions**: always `await AppOverlay.confirm(...)` before
  deletes, unpublishes, or irreversible operations. The function is async — mark the
  containing function `async`.
- **Never** add a per-page success/error overlay. If you find a `.success-overlay`,
  `.error-message`, or inline `alert()` in new code, replace it with `AppOverlay`.

### Adding AppOverlay to a standalone page

For pages that don't import `shared-layout.js` (e.g., a new standalone landing page),
paste the `.app-overlay` CSS into the page `<style>` block and the `window.AppOverlay`
IIFE into a `<script>` tag. The CSS lives in `static/shared-layout.css`
(lines 278-381) and the JS in `static/shared-layout.js`. Both are ~80-40 lines. Since
the API is global, there's no conflict if a page loads both the shared and inline
versions.

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
  - POST `/api/admin/members` - create member for a specific user (admin only)
  - POST `/api/admin/members/bulk-upload/` - bulk member upload via CSV (admin only)
  - GET `/api/admin/members/csv-template/` - download CSV template for bulk upload
  - GET `/api/admin/export/members` - export members CSV (password-protected zip)
  - GET `/api/admin/export/users` - export users CSV (password-protected zip)
  - GET `/api/admin/stats` - dashboard statistics
  - POST `/api/admin/file-resources/` - upload file (multipart, server computes path)
  - GET `/api/admin/file-resources/` - list file resources (cached)
- **Job Adverts**:
  - GET `/api/job-adverts/` - public list (auth required, filters expired/30-day)
  - POST `/api/job-adverts/create/` - create advert (admin only, file optional)
  - GET/DELETE `/api/job-adverts/<int:advert_id>/` - advert detail (admin only)

## Admin Page Patterns

The admin page (`templates/admin.html`) has its own patterns distinct from the shared-layout system:

- **Layout**: Uses `.card` sections with `.form-grid` for inputs, `.pagination` for tables
- **Pagination**: Client-side only — `paginate()`, `renderPagination()`, `goPage()` helpers
  - State: `ALL_USERS`, `ALL_JOB_ADVERTS` arrays + `usersPage`, `jobAdvertsPage` counters
  - `ADMIN_PER_PAGE = 10`
- **File upload**: Two-step pattern — upload file via `FormData` to `/api/admin/file-resources/`,
  get `id`, then POST with `file_id` to the resource-creation endpoint
- **Bulk upload**: CSV via `FormData`, server returns `{created, skipped, errors}` report
- **Tables**: Inline editing with `data-field` and `data-user-id` attributes; update via PATCH

## Database

- Uses PostgreSQL (configured via `DATABASE_URL` in `.env`)
- Tables: `users`, `members`, `profiles`, `file_resources`, `job_adverts` (matches existing Node project schema)
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
- `MEDIA_URL = '/media/'` and `MEDIA_ROOT = BASE_DIR / 'media'` — uploaded files served in DEBUG only
- CSV exports use `_encrypt_and_stream_csv()` — wraps CSV in a password-protected AES zip, returns JSON with base64 + password
- Login response uses `token` (access) and `refresh` keys — not `access`/`refresh` like default simplejwt
- `Member.user` is a required ForeignKey — bulk uploads auto-create placeholder users (role=user, status=pending) with random emails
- For production, set `DEBUG=False` and ensure `ALLOWED_HOSTS` is set appropriately