"""Context processors inject data into every template."""
from pages.auth import get_session_user


def current_user(request):
    """Inject current_user into templates."""
    user = get_session_user(request)
    return {'current_user': user}


def sidebar_links(request):
    """Inject sidebar_links based on user role."""
    user = get_session_user(request)
    links = []
    if user:
        if user.role == 'admin':
            links = [
                {'name': 'Dashboard', 'url': '/dashboard', 'active_path': '/dashboard'},
                {'name': 'Members', 'url': '/members', 'active_path': '/members'},
                {'name': 'Jobs', 'url': '/jobs', 'active_path': '/jobs'},
                {'name': 'Admin', 'url': '/admin', 'active_path': '/admin'},
            ]
        else:
            links = [
                {'name': 'Dashboard', 'url': '/dashboard', 'active_path': '/dashboard'},
                {'name': 'Register', 'url': '/register', 'active_path': '/register'},
                {'name': 'Jobs', 'url': '/jobs', 'active_path': '/jobs'},
            ]
    return {'sidebar_links': links}
