from django.urls import path, include, re_path
from django.views.generic import TemplateView

# Clean URL routes matching the frontend links in shared-layout.js
def tpl(name):
    return TemplateView.as_view(template_name=name)

urlpatterns = [
    path('api/', include('api.urls')),

    # Auth pages
    path('',          tpl('index.html')),
    path('login',     tpl('login.html')),
    path('signup',    tpl('signup.html')),

    # Protected app pages
    path('dashboard', tpl('dashboard.html')),
    path('register',  tpl('data-form.html')),
    path('admin-panel', tpl('admin.html')),
    path('admin', tpl('admin.html')),
    path('data-form', tpl('data-form.html')),

    # Legacy .html paths (backwards compat if any bookmarks exist)
    path('dashboard.html',  tpl('dashboard.html')),
    path('data-form.html',  tpl('data-form.html')),
    path('admin.html',      tpl('admin.html')),
    path('login.html',      tpl('login.html')),
    path('signup.html',     tpl('signup.html')),
]
