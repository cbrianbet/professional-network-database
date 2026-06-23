import contextlib
from django.db import models
from django.contrib.auth.hashers import make_password
import os
from django.conf import settings


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

    @classmethod
    def create_user(cls, email, password, name=None, role='user', status='active'):
        """Create and return a new user with the given email and password."""
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')

        user = cls(
            email=email.lower(),
            name=name or '',
            role=role,
            status=status
        )
        user.set_password(password)
        user.save()
        return user


class Member(models.Model):
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female')]
    STATUS_CHOICES = [
        'employed (full-time)',
        'employed (part-time)',
        'self-employed / business owner',
        'on internship',
        'on attachment',
        'on voluntary / community service',
        'on contract terms',
        'on casual terms',
        'tsc transfer request',
        'active application',
        'shortlisted',
        'attended interview',
        'unemployed (actively seeking)',
        'unemployed (not seeking)',
        'student',
        'retired'
    ]
    """Mirrors the `members` table."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='members')
    name = models.TextField()
    phone = models.TextField()
    email = models.TextField()
    age = models.IntegerField()
    gender = models.TextField(choices=GENDER_CHOICES, default='')
    national_id = models.TextField(unique=True)
    sub_location = models.TextField(blank=True, default='')
    location = models.TextField(blank=True, default='')
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
    # New fields for diaspora and professional bodies
    diaspora = models.BooleanField(default=False)
    profession_bodies = models.JSONField(default=list, blank=True)  # list of strings
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'members'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class FileResource(models.Model):
    """Model for uploaded file resources."""
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('jpeg', 'JPEG'),
        ('png', 'PNG'),
    ]

    PERMISSION_LEVEL_CHOICES = [
        ('public', 'Public'),
        ('authenticated', 'Authenticated'),
        ('private', 'Private'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='file_resources')
    original_filename = models.TextField()
    file_size = models.IntegerField()  # in bytes
    file_type = models.TextField(choices=FILE_TYPE_CHOICES)
    upload_path = models.TextField()  # path to stored file
    thumbnail_path = models.TextField(blank=True, default='')  # path to thumbnail/preview
    uploaded_at = models.DateTimeField(auto_now_add=True)
    permission_level = models.TextField(choices=PERMISSION_LEVEL_CHOICES, default='private')
    uploaded_by = models.TextField(blank=True, default='')  # username who uploaded

    class Meta:
        db_table = 'file_resources'
        ordering = ['-uploaded_at']

    def generate_thumbnail(self):
        """Generate thumbnail for image files or preview for PDFs"""
        if not self.upload_path or not os.path.exists(self.upload_path):
            return

        with contextlib.suppress(Exception):
            from PIL import Image

            # Create thumbnails directory if it doesn't exist
            thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)

            # Generate thumbnail filename
            name, ext = os.path.splitext(os.path.basename(self.upload_path))
            thumbnail_filename = f"{name}_thumb{ext}"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

            # Generate thumbnail based on file type
            if self.file_type.lower() in ['jpeg', 'png']:
                # For images, create thumbnail
                with Image.open(self.upload_path) as img:
                    # Convert to RGB if necessary (for PNG with transparency)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = rgb_img

                    # Create thumbnail
                    img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                    img.save(thumbnail_path, optimize=True, quality=85)

            elif self.file_type.lower() == 'pdf':
                # For PDFs, we would need a PDF library like pdf2image or PyMuPDF
                # For now, we'll just copy the file or create a placeholder
                # In a real implementation, you'd render the first page as an image
                import shutil
                shutil.copy2(self.upload_path, thumbnail_path)

            # Update thumbnail path (relative to MEDIA_ROOT for storage)
            self.thumbnail_path = os.path.relpath(thumbnail_path, settings.MEDIA_ROOT)
            self.save(update_fields=['thumbnail_path'])

    def save(self, *args, **kwargs):
        """Override save to generate thumbnail after saving"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.file_type.lower() in ['jpeg', 'png', 'pdf']:
            self.generate_thumbnail()

    def __str__(self):
        return f"{self.original_filename} ({self.file_type})"


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
