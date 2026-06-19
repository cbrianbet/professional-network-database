from django.test import TestCase
from api.serializers import LoginSerializer, SignupSerializer
from api.models import User, Member


class SerializerTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.create_user(
            email='existing@example.com',
            password='testpass123',
            name='Existing User'
        )
        self.member = Member.objects.create(
            user=self.user,
            name='Existing Member',
            phone='1111111111',
            email='member@example.com',
            age=25,
            national_id='EXISTINGID123',
            status='employed (full-time)'
        )

    def test_login_serializer_with_email(self):
        """Test LoginSerializer validates email correctly"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], 'test@example.com')

    def test_login_serializer_with_national_id(self):
        """Test LoginSerializer validates national ID correctly"""
        data = {
            'email': 'NATIONALID123',  # Using national_id in email field
            'password': 'testpass123'
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        # Should be cleaned up (spaces removed, uppercase)
        self.assertEqual(serializer.validated_data['email'], 'NATIONALID123')

    def test_login_serializer_national_id_with_spaces(self):
        """Test LoginSerializer handles national ID with spaces"""
        data = {
            'email': 'na tio nal id 123',
            'password': 'testpass123'
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        # Should be cleaned up
        self.assertEqual(serializer.validated_data['email'], 'NATIONALID123')

    def test_login_serializer_missing_password(self):
        """Test LoginSerializer requires password"""
        data = {
            'email': 'test@example.com'
            # Missing password
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_login_serializer_missing_email(self):
        """Test LoginSerializer requires email/national_id"""
        data = {
            'password': 'testpass123'
            # Missing email/national_id
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_signup_serializer_with_email(self):
        """Test SignupSerializer works with email"""
        data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'securepass123'
        }
        serializer = SignupSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.name, 'New User')

    def test_signup_serializer_with_national_id(self):
        """Test SignupSerializer works with national ID"""
        data = {
            'name': 'New User',
            'national_id': 'NEWNATIONALID456',
            'password': 'securepass123'
        }
        serializer = SignupSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, '')  # Email optional when national_id provided
        self.assertEqual(user.name, 'New User')
        # Should have created a member record
        self.assertTrue(Member.objects.filter(national_id='NEWNATIONALID456').exists())

    def test_signup_serializer_requires_at_least_one_identifier(self):
        """Test SignupSerializer requires email or national_id"""
        data = {
            'name': 'New User',
            'password': 'securepass123'
            # Missing both email and national_id
        }
        serializer = SignupSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_signup_serializer_duplicate_email(self):
        """Test SignupSerializer rejects duplicate email"""
        data = {
            'name': 'Another User',
            'email': 'existing@example.com',  # Already exists
            'password': 'securepass123'
        }
        serializer = SignupSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_signup_serializer_duplicate_national_id(self):
        """Test SignupSerializer rejects duplicate national ID"""
        data = {
            'name': 'Another User',
            'national_id': 'EXISTINGID123',  # Already exists
            'password': 'securepass123'
        }
        serializer = SignupSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('national_id', serializer.errors)