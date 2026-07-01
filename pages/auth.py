"""Session-based authentication for server-rendered pages."""
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from api.models import User


def login_user(request, user):
    """Store user ID in session (7-day lifetime, matching JWT)."""
    request.session['user_id'] = user.id
    request.session.set_expiry(60 * 60 * 24 * 7)


def get_session_user(request):
    """Retrieve user from session. Returns None if not authenticated."""
    uid = request.session.get('user_id')
    if not uid:
        return None
    try:
        return User.objects.get(pk=uid, status__in=['active', 'pending'])
    except User.DoesNotExist:
        return None


def logout_user(request):
    """Clear session."""
    request.session.flush()


def login_required(view_func):
    """Decorator: redirect unauthenticated users to /login?next=..."""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        user = get_session_user(request)
        if not user:
            return redirect(f"{reverse('login')}?next={request.path}")
        request.user = user
        return view_func(request, *args, **kwargs)
    return wrapped


def admin_required(view_func):
    """Decorator: login_required + admin role check."""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        user = get_session_user(request)
        if not user:
            return redirect(f"{reverse('login')}?next={request.path}")
        if user.role != 'admin':
            return redirect(reverse('dashboard'))
        request.user = user
        return view_func(request, *args, **kwargs)
    return wrapped
