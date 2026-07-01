SHELL_LINKS = [
    {'href': '/dashboard', 'label': 'Dashboard', 'route': 'dashboard'},
    {'href': '/register', 'label': 'Register', 'route': 'register'},
    {'href': '/admin', 'label': 'Admin', 'route': 'admin', 'admin_only': True},
    {'href': '/jobs', 'label': 'Jobs', 'route': 'jobs'},
]


def shell_context(request):
    user = getattr(request, 'user', None)
    is_authenticated = getattr(user, 'is_authenticated', False)
    is_admin = is_authenticated and getattr(user, 'role', None) == 'admin'
    links = [link for link in SHELL_LINKS if not link.get('admin_only') or is_admin]
    return {
        'shell_links': links,
        'current_user': user if is_authenticated else None,
        'session_jwt': request.session.get('_jwt_access', '') if is_authenticated else '',
    }
