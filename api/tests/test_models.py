from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from api.models import User, Member


class MemberModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )

    def test_member_status_choices(self):
        """Test that Member model accepts the new status choices"""
        # Test that the new statuses are valid choices
        statuses_to_test = [
            'on contract terms',
            'on casual terms',
            'tsc transfer request'
        ]

        for status in statuses_to_test:
            member = Member.objects.create(
                user=self.user,
                name='Test Member',
                phone='1234567890',
                email='member@example.com',
                age=25,
                national_id=f'ID{status.replace(" ", "")}123',  # Unique national ID
                status=status
            )
            self.assertEqual(member.status, status)

    def test_member_status_default_behavior(self):
        """Test that Member model still works with existing statuses"""
        member = Member.objects.create(
            user=self.user,
            name='Test Member 2',
            phone='0987654321',
            email='member2@example.com',
            age=30,
            national_id='NATIONALID456',
            status='employed (full-time)'
        )
        self.assertEqual(member.status, 'employed (full-time)')

    def test_national_id_uniqueness(self):
        """Test that national_id field enforces uniqueness"""
        # Create first member with a national_id
        Member.objects.create(
            user=self.user,
            name='Test Member 1',
            phone='1111111111',
            email='member1@example.com',
            age=25,
            national_id='UNIQUEID123',
            status='employed (full-time)'
        )

        # Try to create another user/member with the same national_id
        user2 = User.create_user(
            email='test2@example.com',
            password='testpass123',
            name='Test User 2'
        )

        with self.assertRaises(Exception):  # Could be IntegrityError or ValidationError
            Member.objects.create(
                user=user2,
                name='Test Member 2',
                phone='2222222222',
                email='member2@example.com',
                age=35,
                national_id='UNIQUEID123',  # Duplicate national_id
                status='employed (part-time)'
            )


class UserModelTest(TestCase):
    def test_user_creation(self):
        """Test basic user creation"""
        user = User.create_user(
            email='user@example.com',
            password='password123',
            name='Test User'
        )
        self.assertEqual(user.email, 'user@example.com')
        self.assertTrue(user.check_password('password123'))
        self.assertEqual(user.role, 'user')  # Default role
        self.assertEqual(user.status, 'active')  # Default status