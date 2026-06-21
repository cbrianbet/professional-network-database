from rest_framework import serializers
from .models import User, Member, Profile, FileResource


# ── User ─────────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'status', 'created_at']


class SignupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False)
    national_id = serializers.CharField(max_length=50, required=False)
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_email(self, value):
        if value:  # Only validate if provided
            value = value.lower().strip()
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError('Email is already registered.')
            return value
        return value

    def validate_national_id(self, value):
        if value:  # Only validate if provided
            value = value.replace(' ', '').upper()
            if Member.objects.filter(national_id=value).exists():
                raise serializers.ValidationError('National ID is already registered.')
            return value
        return value

    def validate(self, attrs):
        # Ensure at least one identifier is provided
        email = attrs.get('email')
        national_id = attrs.get('national_id')
        if not email and not national_id:
            raise serializers.ValidationError('Either email or national ID must be provided.')
        return attrs

    def create(self, validated_data):
        user = User(
            name=validated_data['name'].strip(),
            email=validated_data.get('email', '').lower() if validated_data.get('email') else '',
            status='pending',  # New users start as pending approval
        )
        user.set_password(validated_data['password'])
        user.save()

        # Create member record if national_id provided
        national_id = validated_data.get('national_id')
        if national_id:
            national_id = national_id.replace(' ', '').upper()
            # Use provided name for member, empty strings for other required text fields, 0 for age
            Member.objects.create(
                user=user,
                name=validated_data['name'].strip(),
                phone='',
                email='',
                age=0,
                national_id=national_id
            )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        # Convert to lowercase for consistency and strip whitespace
        value = value.lower().strip()

        # Check if it looks like an email (contains @)
        if '@' in value:
            # Validate as email
            if not value:
                raise serializers.ValidationError('Email is required.')
            # Basic email validation - should have @ and at least one . after @
            if '@' not in value or '.' not in value.split('@')[1]:
                raise serializers.ValidationError('Enter a valid email address.')
            return value
        else:
            # Treat as national_id - basic validation
            if not value:
                raise serializers.ValidationError('National ID is required.')
            # Remove spaces and convert to uppercase for consistency
            value = value.replace(' ', '').upper()
            if len(value) < 6:  # Assuming minimum national ID length
                raise serializers.ValidationError('National ID is too short.')
            return value


class AdminCreateUserSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    role = serializers.ChoiceField(choices=['user', 'admin'], default='user')
    status = serializers.ChoiceField(choices=['active', 'pending', 'disabled'], default='active')

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('Email is already registered.')
        return value.lower()

    def create(self, validated_data):
        user = User(
            name=validated_data['name'].strip(),
            email=validated_data['email'],
            role=validated_data.get('role', 'user'),
            status=validated_data.get('status', 'active'),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class AdminUpdateUserSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    email = serializers.EmailField(required=False)
    role = serializers.ChoiceField(choices=['user', 'admin'], required=False)
    status = serializers.ChoiceField(choices=['active', 'pending', 'disabled'], required=False)

    def validate_email(self, value):
        return value.lower()

    def update(self, instance, validated_data):
        email = validated_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({'email': 'Email is already registered.'})
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance


# ── Member ────────────────────────────────────────────────────────────────────

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'


class MemberWriteSerializer(serializers.Serializer):
    name = serializers.CharField()
    phone = serializers.CharField()
    email = serializers.EmailField()
    age = serializers.IntegerField()
    nationalId = serializers.CharField(source='national_id')
    gender = serializers.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')])
    subLocation = serializers.CharField(source='sub_location', allow_blank=True, default='')
    location = serializers.CharField(allow_blank=True, default='')
    education = serializers.CharField(allow_blank=True, default='')
    formFourYear = serializers.IntegerField(source='form_four_year', allow_null=True, required=False)
    kcse = serializers.CharField(allow_blank=True, default='')
    institution = serializers.CharField(allow_blank=True, default='')
    course = serializers.CharField(allow_blank=True, default='')
    graduation = serializers.IntegerField(allow_null=True, required=False)
    status = serializers.CharField()
    employer = serializers.CharField(allow_blank=True, default='')
    career = serializers.CharField()
    skills = serializers.ListField(child=serializers.CharField(), default=list)

    def validate(self, data):
        required = ['name', 'phone', 'email', 'age', 'national_id', 'career', 'status']
        for field in required:
            if not data.get(field):
                raise serializers.ValidationError({field: 'This field is required.'})
        return data

    def create(self, validated_data):
        user = self.context['user']
        return Member.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance


# ── Profile ───────────────────────────────────────────────────────────────────

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class ProfileWriteSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email = serializers.EmailField()
    headline = serializers.CharField(allow_blank=True, default='')
    location = serializers.CharField(allow_blank=True, default='')
    skills = serializers.ListField(child=serializers.CharField(), default=list)
    summary = serializers.CharField(allow_blank=True, default='')

    def create(self, validated_data):
        user = self.context['user']
        return Profile.objects.create(user=user, **validated_data)


# ── FileResource ─────────────────────────────────────────────────────────────

class FileResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileResource
        fields = '__all__'


class FileResourceWriteSerializer(serializers.Serializer):
    original_filename = serializers.CharField()
    file_size = serializers.IntegerField()  # in bytes
    file_type = serializers.ChoiceField(choices=[
        ('pdf', 'PDF'),
        ('jpeg', 'JPEG'),
        ('png', 'PNG'),
    ])
    upload_path = serializers.CharField()  # path to stored file
    permission_level = serializers.ChoiceField(choices=[
        ('public', 'Public'),
        ('authenticated', 'Authenticated'),
        ('private', 'Private'),
    ], default='private')
    uploaded_by = serializers.CharField(allow_blank=True, default='')  # username who uploaded


class BulkFileResourceOperationSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=1000  # Reasonable limit for bulk operations
    )
    action = serializers.ChoiceField(choices=[
        ('delete', 'Delete'),
        ('change_permission', 'Change Permission Level')
    ])
    parameters = serializers.DictField(
        required=False,
        default=dict
    )

    def validate_ids(self, value):
        """Validate that all IDs correspond to existing file resources"""
        # Check if all IDs exist in the database
        existing_ids = set(FileResource.objects.filter(id__in=value).values_list('id', flat=True))
        input_ids = set(value)
        missing_ids = input_ids - existing_ids
        if missing_ids:
            raise serializers.ValidationError(
                f"The following file resource IDs do not exist: {sorted(missing_ids)}"
            )
        return value

    def validate_parameters(self, value):
        """Validate parameters based on action"""
        action = self.initial_data.get('action')
        if action == 'change_permission':
            permission_level = value.get('permission_level')
            if permission_level not in dict(FileResource.PERMISSION_LEVEL_CHOICES):
                raise serializers.ValidationError(
                    f"permission_level must be one of: {list(dict(FileResource.PERMISSION_LEVEL_CHOICES).keys())}"
                )
        return value

    def validate(self, data):
        required = ['original_filename', 'file_size', 'file_type', 'upload_path']
        for field in required:
            if data.get(field) is None:
                raise serializers.ValidationError({field: 'This field is required.'})
        return data

    def create(self, validated_data):
        user = self.context['user']
        return FileResource.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance
