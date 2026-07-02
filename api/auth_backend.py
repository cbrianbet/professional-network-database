"""
Custom SimpleJWT token backend that works with our non-Django-auth User model.
"""
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import authentication, exceptions

from .models import User


def get_tokens_for_user(user: User) -> dict:
    """Return access + refresh token pair for a User instance."""
    refresh = RefreshToken()
    refresh['user_id'] = user.id
    refresh['email'] = user.email
    refresh['role'] = user.role
    refresh['status'] = user.status
    return {
        'refresh': str(refresh),
        'token': str(refresh.access_token),   # keep key name = "token" for frontend compat
    }


class SessionAuthentication(authentication.BaseAuthentication):
    """Authenticate browser requests using the session user id."""

    def authenticate(self, request):
        user_id = request.session.get('_auth_user_id')
        if not user_id:
            return None
        try:
            user = User.objects.get(pk=user_id, status='active')
        except User.DoesNotExist:
            return None
        return (user, None)


class CustomJWTAuthentication(authentication.BaseAuthentication):
    """
    Reads Bearer token, verifies it with SimpleJWT, then loads our custom User.
    Sets request.user to the User model instance (not Django's auth.User).
    """

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).split()
        if not header or header[0].lower() != b'bearer':
            return None
        if len(header) != 2:
            raise exceptions.AuthenticationFailed('Invalid token header.')

        raw_token = header[1]
        try:
            validated = JWTAuthentication().get_validated_token(raw_token)
        except TokenError as e:
            raise exceptions.AuthenticationFailed(str(e))

        user_id = validated.get('user_id')
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found.')

        if user.status == 'disabled':
            raise exceptions.AuthenticationFailed('Account is disabled.')

        return (user, validated)
