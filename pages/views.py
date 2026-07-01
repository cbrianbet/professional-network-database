"""Server-rendered page views."""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from pages.auth import get_session_user, login_user, logout_user, login_required
from pages.forms import LoginForm, SignupForm
from api.models import User, Member


def index_view(request):
    """Homepage: redirect authenticated users to dashboard, others to login."""
    user = get_session_user(request)
    if user:
        return redirect('dashboard')
    return redirect('login')


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """
    Login page: GET shows form, POST authenticates.
    Redirect authenticated users to dashboard.
    """
    user = get_session_user(request)
    if user:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']

            # Try to get user by email or national_id
            user = None
            if '@' in identifier:
                # Login by email
                try:
                    user = User.objects.get(email=identifier)
                except User.DoesNotExist:
                    pass
            else:
                # Login by national_id - find user through member record
                try:
                    member = Member.objects.get(national_id=identifier)
                    user = member.user
                except Member.DoesNotExist:
                    pass

            if not user or not user.check_password(password):
                messages.error(request, 'Invalid credentials.')
                return render(request, 'login.html', {'form': form})

            if user.status == 'pending':
                messages.error(request, 'Account is pending approval. Please contact an administrator.')
                return render(request, 'login.html', {'form': form})

            if user.status == 'disabled':
                messages.error(request, 'Account is disabled.')
                return render(request, 'login.html', {'form': form})

            # Login successful
            login_user(request, user)
            messages.success(request, f'Welcome back, {user.name}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'page_title': 'Login'})


@require_http_methods(['GET', 'POST'])
def signup_view(request):
    """
    Signup page: GET shows form, POST creates user.
    Redirect authenticated users to dashboard.
    """
    user = get_session_user(request)
    if user:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Create user
            user = User(
                name=form.cleaned_data['name'].strip(),
                email=form.cleaned_data['email'].lower().strip() if form.cleaned_data['email'] else '',
                status='pending',  # New users start as pending approval
            )
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Create member if national_id provided
            if form.cleaned_data.get('national_id'):
                national_id = form.cleaned_data['national_id'].replace(' ', '').upper()
                Member.objects.create(
                    user=user,
                    name=form.cleaned_data['name'].strip(),
                    phone='',
                    email='',
                    age=0,
                    national_id=national_id,
                )

            # Auto-login the new user
            login_user(request, user)
            messages.success(request, 'Account created successfully! Your account is pending approval.')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form, 'page_title': 'Sign Up'})


@require_http_methods(['POST'])
def logout_view(request):
    """
    Logout: POST only, clears session and redirects to login.
    """
    user = get_session_user(request)
    if user:
        logout_user(request)
        messages.success(request, 'You have been logged out.')
    return redirect('login')
