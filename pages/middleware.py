from .auth import AnonymousUser, get_user_from_session


class SessionAuthMiddleware:
    """Attach api.models.User (or AnonymousUser) to every request from the session."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = get_user_from_session(request.session)
        return self.get_response(request)
