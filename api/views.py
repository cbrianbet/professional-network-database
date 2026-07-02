import csv
import hashlib
import io
import json
import base64
import pyzipper
import secrets
import string
from cryptography.fernet import Fernet

from django.conf import settings
from django.core.cache import cache
from django.db import models, transaction, IntegrityError
from django.http import StreamingHttpResponse, HttpResponse
from rest_framework import status, exceptions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .auth_backend import CustomJWTAuthentication, get_tokens_for_user
from .models import User, Member, Profile, FileResource, JobAdvert
from .queries import visible_job_adverts
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
    FileResourceSerializer,
    FileResourceWriteSerializer,
    JobAdvertSerializer,
    JobAdvertWriteSerializer,
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
        return Response({'error': 'Email/National ID and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    identifier = sz.validated_data['email']
    password = sz.validated_data['password']

    # Determine if identifier is email or national_id
    if '@' in identifier:
        # Login by email
        try:
            user = User.objects.get(email=identifier.lower())
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        # Login by national_id - find user through their member record
        national_id = identifier.replace(' ', '').upper()
        try:
            member = Member.objects.get(national_id=national_id)
            user = member.user
        except Member.DoesNotExist:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    if user.status == 'pending':
        return Response({'error': 'Account is pending approval. Please contact an administrator.'}, status=status.HTTP_403_FORBIDDEN)

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
        # Filter by status if provided
        status = request.query_params.get('status')
        if status:
            users = users.filter(status=status)
        return Response({'users': UserSerializer(users, many=True).data})

    # POST — create user
    sz = AdminCreateUserSerializer(data=request.data)
    if not sz.is_valid():
        err = next(iter(sz.errors.values()))[0]
        code = status.HTTP_409_CONFLICT if 'already' in str(err) else status.HTTP_400_BAD_REQUEST
        return Response({'error': str(err)}, status=code)
    user = sz.save()
    return Response({'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH', 'DELETE'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def admin_users_update(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response({'user': serializer.data})

    elif request.method == 'PATCH':
        sz = AdminUpdateUserSerializer(data=request.data, partial=True)
        if not sz.is_valid():
            err = next(iter(sz.errors.values()))[0]
            return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = sz.update(user, sz.validated_data)
        except exceptions.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({'error': 'Database integrity error. Possible duplicate entry.'}, status=status.HTTP_409_CONFLICT)
        except Exception as e:  # Keep as safety net for unexpected errors
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'user': UserSerializer(user).data})

    elif request.method == 'DELETE':
        user.delete()
        return Response({'success': True})


# ── Members ───────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@authentication_classes(AUTH)
@permission_classes(AUTHED)
def members_list_create(request):
    if request.method == 'GET':
        print(cache.get("members_list"))
        cache_key = "members_list"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            print("members_list")
            qs = cached_data
        else:
            qs = Member.objects.all() if request.user.role == 'admin' else Member.objects.filter(user=request.user)
            cache.set(cache_key, qs, 3600)  # Cache for 1 hour
        
        return Response({'members': MemberSerializer(qs, many=True).data})

    # POST — admin only
    if request.user.role != 'admin':
        return Response({'error': 'Admin access required to create member records.'}, status=status.HTTP_403_FORBIDDEN)

    sz = MemberWriteSerializer(data=request.data, context={'user': request.user})
    if not sz.is_valid():
        err = next(iter(sz.errors.values()))[0]
        return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)
    member = sz.save()
    # Clear dashboard KPI & members list cache when a new member is created
    cache.delete("dashboard_kpis")
    cache.delete("members_list")
    return Response({'member': MemberSerializer(member).data})


@api_view(['GET', 'PATCH', 'DELETE'])
@authentication_classes(AUTH)
@permission_classes(AUTHED)
def member_detail_update_delete(request, member_id):
    try:
        member = Member.objects.get(pk=member_id)
    except Member.DoesNotExist:
        return Response({'error': 'Member not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Check permissions: admin can access any member, regular users can only access their own
    if request.user.role != 'admin' and member.user != request.user:
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        return Response({'member': MemberSerializer(member).data})

    if request.method == 'DELETE':
        member.delete()
        # Clear dashboard KPI cache when a member is deleted
        cache.delete("dashboard_kpis")
        return Response({'success': True})

    # PATCH
    sz = MemberWriteSerializer(data=request.data, context={'user': request.user})
    if not sz.is_valid():
        err = next(iter(sz.errors.values()))[0]
        return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)
    member = sz.update(member, sz.validated_data)
    # Clear dashboard KPI cache when a member is updated
    cache.delete("dashboard_kpis")
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
    # Clear dashboard KPI cache when a member is created via admin
    cache.delete("dashboard_kpis")
    return Response({'member': MemberSerializer(member).data}, status=status.HTTP_201_CREATED)


# ── Admin — Bulk Member Upload ────────────────────────────────────────────────

@api_view(['GET'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def admin_members_csv_template(request):
    """Return a CSV template with headers and one sample row for bulk upload."""
    columns = [
        'name', 'phone', 'email', 'age', 'national_id', 'career', 'status',
        'gender', 'sub_location', 'location', 'education', 'form_four_year',
        'kcse', 'institution', 'course', 'graduation', 'employer',
        'skills', 'country', 'county', 'profession_bodies',
    ]
    sample = {
        'name': 'Jane Wanjiku',
        'phone': '0712345678',
        'email': 'jane.wanjiku@example.com',
        'age': '32',
        'national_id': '12345678',
        'career': 'Software Engineer',
        'status': 'employed (full-time)',
        'gender': 'female',
        'sub_location': 'Westlands',
        'location': 'Nairobi',
        'education': 'BSc Computer Science',
        'form_four_year': '2014',
        'kcse': 'A',
        'institution': 'University of Nairobi',
        'course': 'Computer Science',
        'graduation': '2018',
        'employer': 'Acme Ltd',
        'skills': 'Python;Django;React',
        'country': 'KE',
        'county': 'Nairobi',
        'profession_bodies': 'IEEE;ACM',
    }
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    writer.writerow(sample)
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="members-bulk-template.csv"'
    return response


@api_view(['POST'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def admin_members_bulk_upload(request):
    """Accept a CSV file and bulk-create members (with placeholder users)."""
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return Response({'error': 'No file uploaded. Please attach a CSV file.'},
                        status=status.HTTP_400_BAD_REQUEST)

    if not uploaded_file.name.lower().endswith('.csv'):
        return Response({'error': 'Only .csv files are accepted.'},
                        status=status.HTTP_400_BAD_REQUEST)

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
    if uploaded_file.size > MAX_FILE_SIZE:
        return Response({'error': 'File too large. Maximum size is 5 MB.'},
                        status=status.HTTP_400_BAD_REQUEST)

    MAX_ROWS = 10_000
    REQUIRED_FIELDS = ['name', 'phone', 'email', 'age', 'national_id', 'career', 'status']
    VALID_STATUSES = [s for s in Member.STATUS_CHOICES]  # already a list of strings
    VALID_GENDERS = ['male', 'female']

    # Track national_ids seen in this upload for within-batch dedup
    seen_national_ids = set()
    # Pre-load existing national_ids for fast lookup
    existing_national_ids = set(
        Member.objects.exclude(national_id='').values_list('national_id', flat=True)
    )

    created = 0
    errors = []

    try:
        decoded = uploaded_file.read().decode('utf-8-sig')
    except UnicodeDecodeError:
        return Response({'error': 'Could not decode file. Please upload a UTF-8 CSV.'},
                        status=status.HTTP_400_BAD_REQUEST)

    reader = csv.DictReader(io.StringIO(decoded))
    if not reader.fieldnames:
        return Response({'error': 'CSV file is empty or has no headers.'},
                        status=status.HTTP_400_BAD_REQUEST)

    for row_num, row in enumerate(reader, start=2):  # row 1 is header
        if row_num > MAX_ROWS + 1:
            errors.append({'row': row_num, 'error': f'Row limit exceeded ({MAX_ROWS} max).'})
            break

        # Strip whitespace from all values
        row = {k.strip(): (v.strip() if v else '') for k, v in row.items() if k}

        row_errors = []

        # Check required fields
        for field in REQUIRED_FIELDS:
            if not row.get(field):
                row_errors.append(f'Missing required field: {field}')

        # Validate status
        if row.get('status') and row['status'] not in VALID_STATUSES:
            row_errors.append(
                f'Invalid status "{row["status"]}". Must be one of: {", ".join(VALID_STATUSES)}'
            )

        # Validate gender if provided
        if row.get('gender') and row['gender'] not in VALID_GENDERS:
            row_errors.append(f'Invalid gender "{row["gender"]}". Must be "male" or "female".')

        # Validate age if provided
        if row.get('age'):
            try:
                age = int(row['age'])
                if age < 1 or age > 150:
                    row_errors.append(f'Invalid age "{row["age"]}". Must be between 1 and 150.')
            except ValueError:
                row_errors.append(f'Invalid age "{row["age"]}". Must be a number.')

        # Validate national_id uniqueness (DB + within batch)
        national_id = row.get('national_id', '').replace(' ', '').upper()
        if national_id:
            if national_id in existing_national_ids:
                row_errors.append(f'National ID "{national_id}" already exists.')
            elif national_id in seen_national_ids:
                row_errors.append(f'National ID "{national_id}" is duplicated in this file.')

        if row_errors:
            errors.append({'row': row_num, 'error': '; '.join(row_errors)})
            continue

        # All checks passed — create placeholder user + member
        try:
            with transaction.atomic():
                # Create placeholder user
                placeholder_email = f"bulk_{national_id.lower()}_{secrets.token_hex(4)}@placeholder.local"
                user = User(
                    name=row['name'].strip(),
                    email=placeholder_email,
                    role='user',
                    status='pending',
                )
                # Generate a random password the admin won't know — user must reset
                temp_password = secrets.token_urlsafe(16)
                user.set_password(temp_password)
                user.save()
                seen_national_ids.add(national_id)
                existing_national_ids.add(national_id)  # prevent future collisions

                # Parse list fields
                skills = [s.strip() for s in row.get('skills', '').split(';') if s.strip()]
                profession_bodies = [p.strip() for p in row.get('profession_bodies', '').split(';') if p.strip()]

                # Parse optional integers
                form_four_year = None
                if row.get('form_four_year'):
                    try:
                        form_four_year = int(row['form_four_year'])
                    except ValueError:
                        pass

                graduation = None
                if row.get('graduation'):
                    try:
                        graduation = int(row['graduation'])
                    except ValueError:
                        pass

                # Country: accept ISO code directly, or try to match name
                country = row.get('country', 'KE') or 'KE'

                Member.objects.create(
                    user=user,
                    name=row['name'].strip(),
                    phone=row.get('phone', '').strip(),
                    email=row.get('email', '').strip().lower(),
                    age=int(row['age']),
                    gender=row.get('gender', ''),
                    national_id=national_id,
                    sub_location=row.get('sub_location', ''),
                    location=row.get('location', ''),
                    education=row.get('education', ''),
                    form_four_year=form_four_year,
                    kcse=row.get('kcse', ''),
                    institution=row.get('institution', ''),
                    course=row.get('course', ''),
                    graduation=graduation,
                    status=row['status'].strip(),
                    employer=row.get('employer', ''),
                    career=row.get('career', '').strip(),
                    skills=skills,
                    country=country,
                    county=row.get('county', ''),
                    profession_bodies=profession_bodies,
                )
                created += 1
        except Exception as e:
            errors.append({'row': row_num, 'error': f'Unexpected error: {str(e)}'})

    # Clear dashboard KPI cache after bulk upload
    cache.delete("dashboard_kpis")
    return Response({
        'created': created,
        'skipped': len(errors),
        'errors': errors,
    })


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
@permission_classes(AUTHED)
def profile_detail(request, profile_id):
    try:
        profile = Profile.objects.get(pk=profile_id)
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Check permissions: admin can access any profile, regular users can only access their own
    if request.user.role != 'admin' and profile.user != request.user:
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

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

def _encrypt_and_stream_csv(rows, columns, filename):
    """Generate CSV, protect it with a password inside a zip,
    and return JSON with the zip blob and the password."""
    # Generate CSV content in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([str(row.get(c, '') or '') for c in columns])
    csv_bytes = output.getvalue().encode('utf-8')

    # Generate a random 10-character alphanumeric password
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(10))

    # Create a zip file in memory with the CSV inside, password-protected
    zip_buffer = io.BytesIO()
    with pyzipper.AESZipFile(
        zip_buffer,
        'w',
        compression=pyzipper.ZIP_DEFLATED,
        encryption=pyzipper.WZ_AES,
    ) as zf:
        zf.setpassword(password.encode('utf-8'))
        zf.writestr(filename, csv_bytes)

    # Get the zip bytes
    zip_bytes = zip_buffer.getvalue()

    # Encode for JSON transport
    b64_zip = base64.b64encode(zip_bytes).decode()

    payload = json.dumps({"password": password, "data": b64_zip})
    return HttpResponse(
        payload,
        content_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}.zip"'},
    )


@authentication_classes(AUTH)
@permission_classes(ADMIN)
def export_members(request):
    columns = [
        'id', 'user_id', 'name', 'email', 'phone', 'age', 'national_id',
        'sub_location', 'education', 'kcse', 'institution', 'course',
        'graduation', 'status', 'employer', 'career', 'skills', 'created_at',
        'country', 'county', 'profession_bodies',
    ]

    def generate_rows():
        for member in Member.objects.all().iterator():
            yield {
                'id': member.id, 'user_id': member.user_id, 'name': member.name, 'email': member.email,
                'phone': member.phone, 'age': member.age, 'national_id': member.national_id,
                'sub_location': member.sub_location, 'education': member.education,
                'kcse': member.kcse, 'institution': member.institution, 'course': member.course,
                'graduation': member.graduation, 'status': member.status, 'employer': member.employer,
                'career': member.career, 'skills': ';'.join(member.skills or []),
                'country': str(member.country.name) if member.country else '',
                'county': str(member.county) if member.county else '',
                'profession_bodies': ';'.join(member.profession_bodies or []),
                'created_at': member.created_at.isoformat(),
            }

    return _encrypt_and_stream_csv(generate_rows(), columns, 'members-export.csv')


@authentication_classes(AUTH)
@permission_classes(ADMIN)
def export_users(request):
    columns = ['id', 'name', 'email', 'role', 'status', 'created_at']

    def generate_rows():
        for user in User.objects.all().iterator():
            yield {
                'id': user.id, 'name': user.name, 'email': user.email,
                'role': user.role, 'status': user.status,
                'created_at': user.created_at.isoformat(),
            }

    return _encrypt_and_stream_csv(generate_rows(), columns, 'users-export.csv')


@api_view(['GET'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def admin_stats(request):
    from django.db.models import Count, Sum, Avg, Max, Min
    from django.utils import timezone
    from datetime import timedelta

    # Basic counts
    total_users = User.objects.count()
    users_by_role = User.objects.values('role').annotate(count=Count('role'))
    users_by_status = User.objects.values('status').annotate(count=Count('status'))

    # Recent users (last 7 days, 30 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    thirty_days_ago = timezone.now() - timedelta(days=30)

    recent_users_7d = User.objects.filter(created_at__gte=seven_days_ago).count()
    recent_users_30d = User.objects.filter(created_at__gte=thirty_days_ago).count()

    # Format the data for easier consumption
    role_counts = {item['role']: item['count'] for item in users_by_role}
    status_counts = {item['status']: item['count'] for item in users_by_status}

    # Storage analytics
    file_stats = FileResource.objects.aggregate(
        total_files=Count('id'),
        total_size=Sum('file_size'),
        avg_file_size=Avg('file_size'),
        max_file_size=Max('file_size'),
        min_file_size=Min('file_size')
    )

    # Files by type
    files_by_type = FileResource.objects.values('file_type').annotate(
        count=Count('id'),
        total_size=Sum('file_size')
    ).order_by('file_type')

    # Files by permission level
    files_by_permission = FileResource.objects.values('permission_level').annotate(
        count=Count('id'),
        total_size=Sum('file_size')
    ).order_by('permission_level')

    # Recent uploads (last 24h, 7d, 30d) using conditional aggregation
    twentyfour_hours_ago = timezone.now() - timedelta(hours=24)
    seven_days_ago = timezone.now() - timedelta(days=7)
    thirty_days_ago = timezone.now() - timedelta(days=30)

    upload_aggregates = FileResource.objects.aggregate(
        recent_uploads_24h=models.Count(
            models.Case(
                models.When(uploaded_at__gte=twentyfour_hours_ago, then=1),
                output_field=models.IntegerField(),
            )
        ),
        recent_uploads_7d=models.Count(
            models.Case(
                models.When(uploaded_at__gte=seven_days_ago, then=1),
                output_field=models.IntegerField(),
            )
        ),
        recent_uploads_30d=models.Count(
            models.Case(
                models.When(uploaded_at__gte=thirty_days_ago, then=1),
                output_field=models.IntegerField(),
            )
        ),
    )

    recent_uploads_24h = upload_aggregates['recent_uploads_24h']
    recent_uploads_7d = upload_aggregates['recent_uploads_7d']
    recent_uploads_30d = upload_aggregates['recent_uploads_30d']

    # Format storage analytics
    files_by_type_dict = {}
    for item in files_by_type:
        files_by_type_dict[item['file_type']] = {
            'count': item['count'],
            'size_bytes': item['total_size'] or 0,
            'size_mb': round((item['total_size'] or 0) / (1024 * 1024), 2)
        }

    files_by_permission_dict = {}
    for item in files_by_permission:
        files_by_permission_dict[item['permission_level']] = {
            'count': item['count'],
            'size_bytes': item['total_size'] or 0,
            'size_mb': round((item['total_size'] or 0) / (1024 * 1024), 2)
        }

    stats = {
        'total_users': total_users,
        'users_by_role': role_counts,
        'users_by_status': status_counts,
        'recent_users': {
            'last_7_days': recent_users_7d,
            'last_30_days': recent_users_30d
        },
        'storage_analytics': {
            'total_files': file_stats['total_files'] or 0,
            'total_size_bytes': file_stats['total_size'] or 0,
            'total_size_mb': round((file_stats['total_size'] or 0) / (1024 * 1024), 2),
            'avg_file_size_bytes': round(file_stats['avg_file_size'] or 0, 2),
            'max_file_size_bytes': file_stats['max_file_size'] or 0,
            'min_file_size_bytes': file_stats['min_file_size'] or 0,
            'by_file_type': files_by_type_dict,
            'by_permission_level': files_by_permission_dict,
            'recent_uploads': {
                'last_24_hours': recent_uploads_24h,
                'last_7_days': recent_uploads_7d,
                'last_30_days': recent_uploads_30d
            }
        }
    }

    return Response(stats)


@api_view(['PATCH'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def admin_user_approve_reject(request, user_id):
    """
    Approve or reject a pending user registration
    Expected data: {'status': 'active' or 'disabled'}
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Only allow approving/rejecting pending users
    if user.status != 'pending':
        return Response({'error': 'Only pending users can be approved or rejected.'}, status=status.HTTP_400_BAD_REQUEST)

    new_status = request.data.get('status')
    if new_status not in ['active', 'disabled']:
        return Response({'error': 'Status must be either \"active\" or \"disabled\".'}, status=status.HTTP_400_BAD_REQUEST)

    user.status = new_status
    user.save()

    return Response({'user': UserSerializer(user).data})


# ── Job Adverts ──────────────────────────────────────────────────────────────

@api_view(['GET'])
@authentication_classes(AUTH)
@permission_classes(AUTHED)
def job_adverts_list(request):
    """Public list — only show adverts that are still visible.

    An advert is visible when:
      - its deadline is in the future (or today), OR
      - it has no deadline AND was posted within the last 30 days.
    """
    adverts = visible_job_adverts()
    return Response({'job_adverts': JobAdvertSerializer(adverts, many=True).data})


@api_view(['POST'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def job_advert_create(request):
    """Admin-only — create a new advert. File upload is optional; provide
    either a file_id (from a prior upload) or a link, or both."""
    sz = JobAdvertWriteSerializer(data=request.data)
    if not sz.is_valid():
        return Response(sz.errors, status=status.HTTP_400_BAD_REQUEST)

    file_resource = None
    file_id = sz.validated_data.get('file_id')
    if file_id:
        try:
            file_resource = FileResource.objects.get(id=file_id)
        except FileResource.DoesNotExist:
            return Response({'error': 'file_id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

    advert = JobAdvert.objects.create(
        title=sz.validated_data['title'],
        company=sz.validated_data['company'],
        link=sz.validated_data.get('link', ''),
        deadline=sz.validated_data.get('deadline'),
        file=file_resource,
        created_by=request.user,
        file_type=sz.validated_data.get('file_type', ''),
    )
    return Response(
        {'job_advert': JobAdvertSerializer(advert).data},
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET', 'DELETE'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def job_advert_detail(request, advert_id):
    try:
        advert = JobAdvert.objects.select_related('file').get(id=advert_id)
    except JobAdvert.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({'job_advert': JobAdvertSerializer(advert).data})

    advert.delete()
    return Response({'success': True})


# ── File Resources ─────────────────────────────────────────────────────────────
@api_view(['GET', 'POST'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def file_resources_list_create(request):
    """
    GET: List all file resources with filtering and search (cached)
    POST: Create a new file resource
    """
    if request.method == 'GET':
        # Get cache version for invalidation strategy
        version = cache.get('file_resources_list_version', 1)
        # Create cache key based on query parameters
        query_params = request.GET.urlencode()
        if query_params:
            # Create stable hash using MD5 (consistent across Python processes)
            query_hash = hashlib.md5(query_params.encode()).hexdigest()
            cache_key = f"file_resources_list_v{version}_{query_hash}_user{request.user.id}"
        else:
            cache_key = f"file_resources_list_v{version}_all_user{request.user.id}"

        # Try to get cached response
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            return Response(cached_response)

        resources = FileResource.objects.all()

        # Filter by file type
        file_type = request.GET.get('file_type')
        if file_type:
            resources = resources.filter(file_type=file_type)

        # Filter by permission level
        permission_level = request.GET.get('permission_level')
        if permission_level:
            resources = resources.filter(permission_level=permission_level)

        # Filter by upload date range
        uploaded_after = request.GET.get('uploaded_after')
        if uploaded_after:
            resources = resources.filter(uploaded_at__gte=uploaded_after)

        uploaded_before = request.GET.get('uploaded_before')
        if uploaded_before:
            resources = resources.filter(uploaded_at__lte=uploaded_before)

        # Search in filename and uploaded_by
        search = request.GET.get('search')
        if search:
            resources = resources.filter(
                models.Q(original_filename__icontains=search) |
                models.Q(uploaded_by__icontains=search)
            )

        # Ordering
        ordering = request.GET.get('ordering', '-uploaded_at')  # Default to newest first
        # Validate ordering field to prevent SQL injection
        valid_ordering_fields = [
            'uploaded_at', '-uploaded_at',
            'original_filename', '-original_filename',
            'file_size', '-file_size',
            'file_type', '-file_type',
            'permission_level', '-permission_level'
        ]
        if ordering in valid_ordering_fields:
            resources = resources.order_by(ordering)
        else:
            # Default to newest first if invalid ordering provided
            resources = resources.order_by('-uploaded_at')

        serializer = FileResourceSerializer(resources, many=True)
        response_data = serializer.data

        # Cache the response for 5 minutes
        cache.set(cache_key, response_data, 300)

        return Response(response_data)

    elif request.method == 'POST':
        # Accept an actual uploaded file (multipart) and compute the storage
        # path server-side. Falls back to the JSON write-serializer when no
        # file is attached (e.g. for programmatic creation).
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            file_type = (request.data.get('file_type') or '').lower()
            if file_type not in ('pdf', 'jpeg', 'png'):
                return Response({'error': 'file_type must be pdf, jpeg, or png.'}, status=status.HTTP_400_BAD_REQUEST)

            # Build a storage path under MEDIA_ROOT/uploads/<type>/<name>
            import os
            from django.utils import timezone
            safe_name = os.path.basename(uploaded_file.name)
            rel_dir = os.path.join('uploads', file_type)
            rel_path = os.path.join(rel_dir, f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{safe_name}")
            abs_dir = os.path.join(settings.MEDIA_ROOT, rel_dir)
            os.makedirs(abs_dir, exist_ok=True)
            abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
            with open(abs_path, 'wb+') as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)

            resource = FileResource.objects.create(
                user=request.user,
                original_filename=uploaded_file.name,
                file_size=uploaded_file.size,
                file_type=file_type,
                upload_path=rel_path,
                permission_level=request.data.get('permission_level', 'authenticated'),
                uploaded_by=request.user.name or request.user.email,
            )
            try:
                cache.incr('file_resources_list_version')
            except ValueError:
                cache.set('file_resources_list_version', 1)
            return Response(FileResourceSerializer(resource).data, status=status.HTTP_201_CREATED)

        serializer = FileResourceWriteSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            resource = serializer.save()
            try:
                cache.incr('file_resources_list_version')
            except ValueError:
                cache.set('file_resources_list_version', 1)
            return Response(FileResourceSerializer(resource).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def file_resource_detail(request, resource_id):
    """
    GET: Get file resource details
    PATCH: Update file resource
    DELETE: Delete file resource
    """
    try:
        resource = FileResource.objects.get(id=resource_id)
    except FileResource.DoesNotExist:
        return Response({'error': 'File resource not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FileResourceSerializer(resource)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = FileResourceWriteSerializer(resource, data=request.data, partial=True, context={'user': request.user})
        if serializer.is_valid():
            resource = serializer.save()
            # Increment cache version to invalidate all file resources list caches
            try:
                cache.incr('file_resources_list_version')
            except ValueError:
                cache.set('file_resources_list_version', 1)
            return Response(FileResourceSerializer(resource).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        resource.delete()
        # Increment cache version to invalidate all file resources list caches
        try:
            cache.incr('file_resources_list_version')
        except ValueError:
            cache.set('file_resources_list_version', 1)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes(AUTH)
@permission_classes(ADMIN)
def file_resources_bulk_delete(request):
    """
    Bulk delete file resources
    Expected data: {'ids': [1, 2, 3, ...]}
    """
    serializer = BulkFileResourceOperationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    ids = serializer.validated_data['ids']
    action = serializer.validated_data['action']
    parameters = serializer.validated_data.get('parameters', {})

    if action == 'delete':
        # Bulk delete
        with transaction.atomic():
            resources_to_delete = FileResource.objects.filter(id__in=ids)
            count = resources_to_delete.count()
            resources_to_delete.delete()
            # Increment cache version to invalidate all file resources list caches
            try:
                cache.incr('file_resources_list_version')
            except ValueError:
                cache.set('file_resources_list_version', 1)

        return Response({
            'deleted_count': count,
            'message': f'Successfully deleted {count} file resource(s)'
        }, status=status.HTTP_200_OK)

    elif action == 'change_permission':
        # Bulk change permission level
        permission_level = parameters.get('permission_level')
        if not permission_level:
            return Response({
                'error': 'permission_level parameter is required for change_permission action'
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            resources_to_update = FileResource.objects.filter(id__in=ids)
            count = resources_to_update.count()
            resources_to_update.update(permission_level=permission_level)
            # Increment cache version to invalidate all file resources list caches
            try:
                cache.incr('file_resources_list_version')
            except ValueError:
                cache.set('file_resources_list_version', 1)

        return Response({
            'updated_count': count,
            'message': f'Successfully updated permission level to {permission_level} for {count} file resource(s)'
        }, status=status.HTTP_200_OK)

    return Response({
        'error': 'Invalid action specified'
    }, status=status.HTTP_400_BAD_REQUEST)
