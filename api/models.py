from django.db import models
from django.contrib.auth.hashers import make_password


class User(models.Model):
    """
    Custom user table — mirrors the existing `users` table.
    We avoid Django's built-in auth.User so the DB schema stays identical
    to the original Node project and migrations are clean.
    """
    ROLE_CHOICES = [('user', 'User'), ('admin', 'Admin')]
    STATUS_CHOICES = [('active', 'Active'), ('pending', 'Pending'), ('disabled', 'Disabled')]

    name = models.TextField()
    email = models.EmailField(unique=True)
    password_hash = models.TextField()
    role = models.TextField(choices=ROLE_CHOICES, default='user')
    status = models.TextField(choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    # ── DRF / Django compatibility shims ─────────────────────────────────
    # DRF's IsAuthenticated calls request.user.is_authenticated
    @property
    def is_authenticated(self):
        return True

    # DRF's IsAdminUser (built-in) checks is_staff — we use our own
    # permission class instead, but add it for safety
    @property
    def is_staff(self):
        return self.role == 'admin'

    @property
    def is_active(self):
        return self.status == 'active'

    # Required by Django's auth machinery in some middleware paths
    @property
    def is_anonymous(self):
        return False

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def set_password(self, raw_password: str):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password_hash)

    def __str__(self):
        return f'{self.name} <{self.email}>'


class Member(models.Model):
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female')]
    """Mirrors the `members` table."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='members')
    name = models.TextField()
    phone = models.TextField()
    email = models.TextField()
    age = models.IntegerField()
    gender = models.TextField(choices=GENDER_CHOICES, default='')
    national_id = models.TextField()
    sub_location = models.TextField(blank=True, default='')
    education = models.TextField(blank=True, default='')
    form_four_year = models.IntegerField(null=True, blank=True)
    kcse = models.TextField(blank=True, default='')
    institution = models.TextField(blank=True, default='')
    course = models.TextField(blank=True, default='')
    graduation = models.IntegerField(null=True, blank=True)
    status = models.TextField()
    employer = models.TextField(blank=True, default='')
    career = models.TextField(blank=True, default='')
    # PostgreSQL text[] stored as a JSON array in Django
    skills = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'members'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Profile(models.Model):
    """Mirrors the `profiles` table."""
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='profiles')
    full_name = models.TextField()
    email = models.TextField()
    headline = models.TextField(blank=True, default='')
    location = models.TextField(blank=True, default='')
    skills = models.JSONField(default=list, blank=True)
    summary = models.TextField(blank=True, default='')
    status = models.TextField(choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'profiles'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name
