from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from pages import views as page_views

urlpatterns = [
    path('api/', include('api.urls')),

    # Auth pages
    path('', page_views.index, name='index'),
    path('login', page_views.login_page, name='login'),
    path('signup', page_views.signup_page, name='signup'),
    path('logout', page_views.logout_page, name='logout'),

    # Protected app pages
    path('dashboard', page_views.dashboard, name='dashboard'),
    path('register', page_views.register, name='register'),
    path('admin-panel', page_views.admin_panel, name='admin-panel'),
    path('admin', page_views.admin_panel, name='admin'),
    path('data-form', page_views.data_form, name='data-form'),
    path('jobs', page_views.jobs, name='jobs'),

    # Legacy .html paths (backwards compat if any bookmarks exist)
    path('dashboard.html', page_views.dashboard, name='dashboard-legacy'),
    path('data-form.html', page_views.data_form, name='data-form-legacy'),
    path('admin.html', page_views.admin_panel, name='admin-legacy'),
    path('login.html', page_views.login_page, name='login-legacy'),
    path('signup.html', page_views.signup_page, name='signup-legacy'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
