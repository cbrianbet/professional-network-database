from django.core.cache import cache
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from api.serializers import SignupSerializer

from .auth import authenticate_credentials, login_user, logout_user
from .decorators import admin_required, login_required
from .queries import visible_job_adverts
from api.models import Member

from django.db import models
from django.db.models import Q
from django.core.cache import cache


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


@require_http_methods(["GET", "POST"])
def signup_page(request):
    if getattr(request.user, "is_authenticated", False):
        return redirect("dashboard")

    error = None
    form_data = {}
    if request.method == "POST":
        form_data = {
            "name": request.POST.get("name", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "national_id": request.POST.get("national_id", "").strip(),
            "password": request.POST.get("password", ""),
        }
        sz = SignupSerializer(data=form_data)
        if not sz.is_valid():
            error = next(iter(sz.errors.values()))[0]
        else:
            user = sz.save()
            login_user(request, user)
            # Clear dashboard KPI cache when new user registers
            cache.delete("dashboard_kpis")
            return redirect("dashboard")

    return render(request, "signup.html", {
        "error": error,
        "form": form_data,
    })


def logout_page(request):
    logout_user(request)
    return redirect('login')

@login_required
def dashboard(request):
    # Try to get cached KPI data
    cache_key = "dashboard_kpis"
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        total, employed, seeking, interns, employed_pct, seeking_pct = cached_data
    else:
        # Fetch all members for KPI calculations
        members = Member.objects.all()
        total = members.count()
        employed = members.filter(
            Q(status__istartswith="employed") |
            Q(status__iexact="self-employed / business owner") |
            Q(status__iexact="on contract terms") |
            Q(status__iexact="on casual terms")
        ).count()
        seeking = members.filter(
            Q(status__icontains="unemployed") |
            Q(status__iexact="active application") |
            Q(status__iexact="shortlisted") |
            Q(status__iexact="attended interview") |
            Q(status__iexact="tsc transfer request")
        ).count()
        interns = members.filter(
            Q(status__icontains="internship") |
            Q(status__icontains="attachment")
        ).count()
        employed_pct = round((employed / total * 100) if total > 0 else 0)
        seeking_pct = round((seeking / total * 100) if total > 0 else 0)
        
        # Cache the results for 1hr (3600 seconds)
        cache.set(cache_key, (total, employed, seeking, interns, employed_pct, seeking_pct), 3600)
    
    return render(request, "dashboard.html", {
        "active_path": "/dashboard",
        "kpi_total": total,
        "kpi_employed": employed,
        "kpi_seeking": seeking,
        "kpi_interns": interns,
        "kpi_employed_pct": employed_pct,
        "kpi_seeking_pct": seeking_pct,
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
