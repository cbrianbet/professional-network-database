from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────
    path('auth/me',     views.me),
    path('auth/signup', views.signup),
    path('auth/login',  views.login),

    # ── Admin — users (GET list, POST create, PATCH update) ────────────────
    path('admin/users',               views.admin_users_list_create),
    path('admin/users/<int:user_id>', views.admin_users_update),

    # ── Admin — members (explicit userId) ─────────────────────────────────
    path('admin/members', views.admin_members_create),

    # ── Admin — exports ───────────────────────────────────────────────────
    path('admin/export/members', views.export_members),
    path('admin/export/users',   views.export_users),

    # ── Members (GET list, POST create) ────────────────────────────────────
    path('members',                 views.members_list_create),
    # ── Member detail (GET, PATCH, DELETE) ────────────────────────────────
    path('members/<int:member_id>', views.member_detail_update_delete),

    # ── Profiles (GET list, POST create) ───────────────────────────────────
    path('profiles',                  views.profiles_list_create),
    # ── Profile detail (PATCH status, DELETE) ─────────────────────────────
    path('profiles/<int:profile_id>', views.profile_detail),
]
