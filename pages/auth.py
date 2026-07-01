"""Session-based authentication for server-rendered pages."""

from api.models import Member, User
from api.auth_backend import get_tokens_for_user


class AnonymousUser:
    """Placeholder for unauthenticated requests."""

    id = None
    role = None
    name = ''
    email = ''
    is_authenticated = False
    is_anonymous = True
    is_active = False
    is_staff = False


def authenticate_credentials(identifier: str, password: str):
    """Return an active user for email/national ID + password, or None."""
    identifier = (identifier or '').strip()
    if not identifier or not password:
        return None

    if '@' in identifier:
        try:
            user = User.objects.get(email=identifier.lower())
        except User.DoesNotExist:
            return None
    else:
        national_id = identifier.replace(' ', '').upper()
        try:
            member = Member.objects.get(national_id=national_id)
            user = member.user
        except Member.DoesNotExist:
            return None

    if not user.check_password(password):
        return None
    if user.status in ('pending', 'disabled'):
        return user, user.status
    return user, None


def login_user(request, user):
    """Establish a session for the given user."""
    request.session['_auth_user_id'] = user.id
    request.session.cycle_key()
    tokens = get_tokens_for_user(user)
    request.session['_jwt_access'] = tokens['token']


def logout_user(request):
    request.session.flush()


def get_user_from_session(session):
    user_id = session.get('_auth_user_id')
    if not user_id:
        return AnonymousUser()
    try:
        return User.objects.get(pk=user_id, status='active')
    except User.DoesNotExist:
        return AnonymousUser()
