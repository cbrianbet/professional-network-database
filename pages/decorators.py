from functools import wraps

from django.shortcuts import redirect


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request.user, 'is_authenticated', False):
            return redirect(f'/login?next={request.path}')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request.user, 'is_authenticated', False):
            return redirect(f'/login?next={request.path}')
        if getattr(request.user, 'role', None) != 'admin':
            return redirect('/dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
