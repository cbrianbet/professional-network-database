from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────
    path('auth/me/',     views.me, name='me'),
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/',  views.login, name='login'),

    # ── Admin — users (GET list, POST create, PATCH update) ────────────────
    path('admin/users/',               views.admin_users_list_create, name='admin-users-list'),
    path('admin/users/<int:user_id>/', views.admin_users_update, name='admin-user-update'),

    # ── Admin — members (explicit userId) ─────────────────────────────────
    path('admin/members/', views.admin_members_create, name='admin-members-create'),
    path('admin/members/bulk-upload/', views.admin_members_bulk_upload, name='admin-members-bulk-upload'),
    path('admin/members/csv-template/', views.admin_members_csv_template, name='members-csv-template'),

    # ── Admin — exports ───────────────────────────────────────────────────
    path('admin/export/members/', views.export_members, name='export-members'),
    path('admin/export/users/',   views.export_users, name='export-users'),

    # ── Admin — statistics ────────────────────────────────────────────────
    path('admin/stats/', views.admin_stats, name='admin-stats'),

    # ── Admin — user approval ─────────────────────────────────────────────
    path('admin/users/<int:user_id>/approve-reject/', views.admin_user_approve_reject, name='admin-user-approve-reject'),

    # ── Job Adverts ─────────────────────────────────────────────────────
    path('job-adverts/',                     views.job_adverts_list, name='job-adverts-list'),        # GET: public list (auth)
    path('job-adverts/create/',              views.job_advert_create, name='job-advert-create'),       # POST: admin create
    path('job-adverts/<int:advert_id>/',     views.job_advert_detail, name='job-advert-detail'),       # GET/DELETE: admin

    # ── Admin — file resources (GET list, POST create) ───────────────────
    path('admin/file-resources/', views.file_resources_list_create, name='file-resource-list'),
    path('admin/file-resources/<int:resource_id>/', views.file_resource_detail, name='file-resource-detail'),
    path('admin/file-resources/bulk/', views.file_resources_bulk_delete, name='file-resource-bulk-operation'),

    # ── Members (GET list, POST create) ────────────────────────────────────
    path('members/',                 views.members_list_create, name='member-list'),
    # ── Member detail (GET, PATCH, DELETE) ─────────────────────────────────
    path('members/<int:member_id>/', views.member_detail_update_delete, name='member-detail'),

    # ── Profiles (GET list, POST create) ───────────────────────────────────
    path('profiles/',                  views.profiles_list_create, name='profile-list'),
    # ── Profile detail (PATCH status, DELETE) ─────────────────────────────
    path('profiles/<int:profile_id>/', views.profile_detail, name='profile-detail'),
]