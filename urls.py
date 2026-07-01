from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from pages import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('login', TemplateView.as_view(template_name='login.html'), name='login'),
    path('signup', TemplateView.as_view(template_name='signup.html'), name='signup'),
    path('logout', views.index_view, name='logout'),
    path('dashboard', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('register', TemplateView.as_view(template_name='data-form.html'), name='register'),
    path('admin-panel', TemplateView.as_view(template_name='admin.html'), name='admin-panel'),
    path('admin', TemplateView.as_view(template_name='admin.html'), name='admin'),
    path('data-form', TemplateView.as_view(template_name='data-form.html'), name='data-form'),
    path('jobs', TemplateView.as_view(template_name='jobs.html'), name='jobs'),
    path('dashboard.html', TemplateView.as_view(template_name='dashboard.html')),
    path('data-form.html', TemplateView.as_view(template_name='data-form.html')),
    path('admin.html', TemplateView.as_view(template_name='admin.html')),
    path('login.html', TemplateView.as_view(template_name='login.html')),
    path('signup.html', TemplateView.as_view(template_name='signup.html')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
