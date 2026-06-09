from rest_framework import serializers
from .models import User, Member, Profile


# ── User ─────────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'status', 'created_at']


class SignupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('Email is already registered.')
        return value.lower()

    def create(self, validated_data):
        user = User(
            name=validated_data['name'].strip(),
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


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
    subLocation = serializers.CharField(source='sub_location', allow_blank=True, default='')
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
