from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from api.serializers import SignupSerializer

from .auth import authenticate_credentials, login_user, logout_user
from .decorators import admin_required, login_required
from .queries import visible_job_adverts


def index(request):
    if getattr(request.user, 'is_authenticated', False):
        return redirect('dashboard')
    return redirect('login')


@require_http_methods(['GET', 'POST'])
def login_page(request):
    if getattr(request.user, 'is_authenticated', False):
        return redirect('dashboard')

    error = None
    identifier = ''
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '')
        result = authenticate_credentials(identifier, password)
        if result is None:
            error = 'Invalid credentials.'
        else:
            user, status_error = result
            if status_error == 'pending':
                error = 'Account is pending approval. Please contact an administrator.'
            elif status_error == 'disabled':
                error = 'Account is disabled.'
            else:
                login_user(request, user)
                next_url = request.GET.get('next') or request.POST.get('next') or '/dashboard'
                return redirect(next_url)

    return render(request, 'login.html', {
        'error': error,
        'identifier': identifier,
        'next': request.GET.get('next', ''),
    })


@require_http_methods(['GET', 'POST'])
def signup_page(request):
    if getattr(request.user, 'is_authenticated', False):
        return redirect('dashboard')

    error = None
    form_data = {}
    if request.method == 'POST':
        form_data = {
            'name': request.POST.get('name', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'national_id': request.POST.get('national_id', '').strip(),
            'password': request.POST.get('password', ''),
        }
        sz = SignupSerializer(data=form_data)
        if not sz.is_valid():
            error = next(iter(sz.errors.values()))[0]
        else:
            user = sz.save()
            login_user(request, user)
            return redirect('dashboard')

    return render(request, 'signup.html', {
        'error': error,
        'form': form_data,
    })


@require_http_methods(['GET', 'POST'])
def logout_page(request):
    logout_user(request)
    return redirect('login')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {
        'active_path': '/dashboard',
    })


@login_required
def register(request):
    return render(request, 'data-form.html', {
        'active_path': '/register',
    })


@login_required
def data_form(request):
    return render(request, 'data-form.html', {
        'active_path': '/data-form',
    })


@admin_required
def admin_panel(request):
    return render(request, 'admin.html', {
        'active_path': '/admin',
    })


@login_required
def jobs(request):
    return render(request, 'jobs.html', {
        'active_path': '/jobs',
        'page_title': 'Job Opportunities',
        'job_adverts': visible_job_adverts(),
    })
