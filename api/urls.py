from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────
    path('auth/me/',     views.me),
    path('auth/signup/', views.signup),
    path('auth/login/',  views.login),

    # ── Admin — users (GET list, POST create, PATCH update) ────────────────
    path('admin/users/',               views.admin_users_list_create),
    path('admin/users/<int:user_id>/', views.admin_users_update),

    # ── Admin — members (explicit userId) ─────────────────────────────────
    path('admin/members/', views.admin_members_create),
    path('admin/members/bulk-upload/', views.admin_members_bulk_upload),
    path('admin/members/csv-template/', views.admin_members_csv_template),

    # ── Admin — exports ───────────────────────────────────────────────────
    path('admin/export/members/', views.export_members),
    path('admin/export/users/',   views.export_users),

    # ── Admin — statistics ────────────────────────────────────────────────
    path('admin/stats/', views.admin_stats),

    # ── Admin — user approval ─────────────────────────────────────────────
    path('admin/users/<int:user_id>/approve-reject/', views.admin_user_approve_reject),

    # ── Job Adverts ─────────────────────────────────────────────────────
    path('job-adverts/',                     views.job_adverts_list),        # GET: public list (auth)
    path('job-adverts/create/',              views.job_advert_create),       # POST: admin create
    path('job-adverts/<int:advert_id>/',     views.job_advert_detail),       # GET/DELETE: admin

    # ── Admin — file resources (GET list, POST create) ───────────────────
    path('admin/file-resources/', views.file_resources_list_create),
    path('admin/file-resources/<int:resource_id>/', views.file_resource_detail),
    path('admin/file-resources/bulk/', views.file_resources_bulk_delete),

    # ── Members (GET list, POST create) ────────────────────────────────────
    path('members/',                 views.members_list_create),
    # ── Member detail (GET, PATCH, DELETE) ─────────────────────────────────
    path('members/<int:member_id>/', views.member_detail_update_delete),

    # ── Profiles (GET list, POST create) ───────────────────────────────────
    path('profiles/',                  views.profiles_list_create),
    # ── Profile detail (PATCH status, DELETE) ─────────────────────────────
    path('profiles/<int:profile_id>/', views.profile_detail),
]