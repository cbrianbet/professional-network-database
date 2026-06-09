"""
Management command: seed_admin
Creates the initial admin user from ADMIN_EMAIL / ADMIN_PASSWORD env vars.
Run automatically from the Railway start command (see Procfile).
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import User


class Command(BaseCommand):
    help = 'Seed initial admin user from environment variables.'

    def handle(self, *args, **options):
        email = getattr(settings, 'ADMIN_EMAIL', '').strip().lower()
        password = getattr(settings, 'ADMIN_PASSWORD', '').strip()

        if not email or not password:
            self.stdout.write('ADMIN_EMAIL / ADMIN_PASSWORD not set — skipping admin seed.')
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(f'Admin already exists: {email}')
            return

        user = User(name='Administrator', email=email, role='admin', status='active')
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Created admin user: {email}'))
