import csv

from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .auth_backend import CustomJWTAuthentication, get_tokens_for_user
from .models import User, Member, Profile
from .permissions import IsAdminUser
from .serializers import (
    UserSerializer,
    SignupSerializer,
    LoginSerializer,
    AdminCreateUserSerializer,
    AdminUpdateUserSerializer,
    MemberSerializer,
    MemberWriteSerializer,
    ProfileSerializer,
    ProfileWriteSerializer,
)

AUTH  = [CustomJWTAuthentication]
AUTHED = [IsAuthenticated]
ADMIN  = [IsAdminUser]


# ── Auth ──────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@authentication_classes(AUTH)
@permission_classes(AUTHED)
def me(request):
    return Response({'user': UserSerializer(request.user).data})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def signup(request):
    sz = SignupSerializer(data=request.data)
    if not sz.is_valid():
        err = next(iter(sz.errors.values()))[0]
        code = status.HTTP_409_CONFLICT if 'already' in str(err) else status.HTTP_400_BAD_REQUEST
        return Response({'error': str(err)}, status=code)
    user = sz.save()
    tokens = get_tokens_for_user(user)
    return Response({**tokens, 'user': UserSerializer(user).data})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    sz = LoginSerializer(data=request.data)
    if not sz.is_valid():
        return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    email    = sz.validated_data['email'].lower()
    password = sz.validated_data['password']

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    if user.status == 'disabled':
        return Response({'error': 'Account is disabled.'}, status=status.HTTP_403_FORBIDDEN)

    tokens = get_tokens_for_user(user)
    return Response({**tokens, 'user': UserSerializer(user).data})


# ── Admin — Users ─────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def admin_users_list_create(request):
    if request.method == 'GET':
        users = User.objects.all()
        return Response({'users': UserSerializer(users, many=True).data})

    # POST — create user
    sz = AdminCreateUserSerializer(data=request.data)
    if not sz.is_valid():
        err = next(iter(sz.errors.values()))[0]
        code = status.HTTP_409_CONFLICT if 'already' in str(err) else status.HTTP_400_BAD_REQUEST
        return Response({'error': str(err)}, status=code)
    user = sz.save()
    return Response({'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def admin_users_update(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    sz = AdminUpdateUserSerializer(data=request.data, partial=True)
    if not sz.is_valid():
        err = next(iter(sz.errors.values()))[0]
        return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = sz.update(user, sz.validated_data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)

    return Response({'user': UserSerializer(user).data})


# ── Members ───────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@authentication_classes(AUTH)
@permission_classes(AUTHED)
def members_list_create(request):
    if request.method == 'GET':
        qs = Member.objects.all() if request.user.role == 'admin' else Member.objects.filter(user=request.user)
        return Response({'members': MemberSerializer(qs, many=True).data})

    # POST — admin only
    if request.user.role != 'admin':
        return Response({'error': 'Admin access required to create member records.'}, status=status.HTTP_403_FORBIDDEN)

    sz = MemberWriteSerializer(data=request.data, context={'user': request.user})
    if not sz.is_valid():
        err = next(iter(sz.errors.values()))[0]
        return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)
    member = sz.save()
    return Response({'member': MemberSerializer(member).data})


@api_view(['GET', 'PATCH', 'DELETE'])
@authentication_classes(AUTH)
@permission_classes(AUTHED)
def member_detail_update_delete(request, member_id):
    # GET and DELETE are admin-only; PATCH is also admin-only per original logic
    if request.user.role != 'admin':
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        member = Member.objects.get(pk=member_id)
    except Member.DoesNotExist:
        return Response({'error': 'Member not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({'member': MemberSerializer(member).data})

    if request.method == 'DELETE':
        member.delete()
        return Response({'success': True})

    # PATCH
    sz = MemberWriteSerializer(data=request.data, context={'user': request.user})
    if not sz.is_valid():
        err = next(iter(sz.errors.values()))[0]
        return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)
    member = sz.update(member, sz.validated_data)
    return Response({'member': MemberSerializer(member).data})


# ── Admin — Members (explicit userId) ─────────────────────────────────────────

@api_view(['POST'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def admin_members_create(request):
    user_id = request.data.get('userId')
    if not user_id:
        return Response({'error': 'userId is required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        target_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    sz = MemberWriteSerializer(data=request.data, context={'user': target_user})
    if not sz.is_valid():
        err = next(iter(sz.errors.values()))[0]
        return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)
    member = sz.save()
    return Response({'member': MemberSerializer(member).data}, status=status.HTTP_201_CREATED)


# ── Profiles ──────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@authentication_classes(AUTH)
@permission_classes(AUTHED)
def profiles_list_create(request):
    if request.method == 'GET':
        qs = Profile.objects.all() if request.user.role == 'admin' else Profile.objects.filter(user=request.user)
        return Response({'profiles': ProfileSerializer(qs, many=True).data})

    sz = ProfileWriteSerializer(data=request.data, context={'user': request.user})
    if not sz.is_valid():
        err = next(iter(sz.errors.values()))[0]
        return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)
    profile = sz.save()
    return Response({'profile': ProfileSerializer(profile).data})


@api_view(['PATCH', 'DELETE'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def profile_detail(request, profile_id):
    try:
        profile = Profile.objects.get(pk=profile_id)
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        profile.delete()
        return Response({'success': True})

    # PATCH
    profile_status = request.data.get('status')
    if not profile_status:
        return Response({'error': 'Status is required.'}, status=status.HTTP_400_BAD_REQUEST)
    profile.status = profile_status
    profile.save()
    return Response({'profile': ProfileSerializer(profile).data})


# ── CSV Exports ───────────────────────────────────────────────────────────────

class _Echo:
    def write(self, value):
        return value


def _stream_csv(rows, columns, filename):
    writer = csv.writer(_Echo())

    def generate():
        yield writer.writerow(columns)
        for row in rows:
            yield writer.writerow([str(row.get(c, '') or '') for c in columns])

    response = StreamingHttpResponse(generate(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@api_view(['GET'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def export_members(request):
    columns = [
        'id', 'user_id', 'name', 'email', 'phone', 'age', 'national_id',
        'sub_location', 'education', 'kcse', 'institution', 'course',
        'graduation', 'status', 'employer', 'career', 'skills', 'created_at',
    ]
    rows = []
    for m in Member.objects.all():
        rows.append({
            'id': m.id, 'user_id': m.user_id, 'name': m.name, 'email': m.email,
            'phone': m.phone, 'age': m.age, 'national_id': m.national_id,
            'sub_location': m.sub_location, 'education': m.education,
            'kcse': m.kcse, 'institution': m.institution, 'course': m.course,
            'graduation': m.graduation, 'status': m.status, 'employer': m.employer,
            'career': m.career, 'skills': ';'.join(m.skills or []),
            'created_at': m.created_at.isoformat(),
        })
    return _stream_csv(rows, columns, 'members-export.csv')


@api_view(['GET'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def export_users(request):
    columns = ['id', 'name', 'email', 'role', 'status', 'created_at']
    rows = []
    for u in User.objects.all():
        rows.append({
            'id': u.id, 'name': u.name, 'email': u.email,
            'role': u.role, 'status': u.status,
            'created_at': u.created_at.isoformat(),
        })
    return _stream_csv(rows, columns, 'users-export.csv')
