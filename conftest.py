"""Shared pytest fixtures for the professional-network-database test suite."""
import pytest
from api.models import User, Member


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    return User.create_user(
        email='admin@test.com',
        password='adminpass123',
        name='Admin User',
        role='admin',
    )


@pytest.fixture
def regular_user(db):
    """Create a regular user for testing."""
    return User.create_user(
        email='user@test.com',
        password='userpass123',
        name='Regular User',
        role='user',
    )


@pytest.fixture
def make_user(db):
    """Factory fixture to create users with custom params."""

    def _make_user(
        email='default@test.com',
        password='pass123',
        name='Test User',
        role='user',
        status='active',
    ):
        return User.create_user(
            email=email, password=password, name=name, role=role, status=status
        )

    return _make_user


@pytest.fixture
def make_member(db, regular_user):
    """Factory fixture to create members with unique national_ids."""
    counter = [0]

    def _make_member(user=None, **overrides):
        counter[0] += 1
        defaults = {
            'user': user or regular_user,
            'name': f'Member {counter[0]}',
            'phone': f'0712345{counter[0]:03d}',
            'email': f'member{counter[0]}@test.com',
            'age': 25,
            'national_id': f'NID{counter[0]:08d}',
            'status': 'employed (full-time)',
        }
        defaults.update(overrides)
        return Member.objects.create(**defaults)

    return _make_member
