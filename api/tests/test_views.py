from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Member


class AuthViewTest(TestCase):
    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()
        self.user = User.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        self.member = Member.objects.create(
            user=self.user,
            name='Test Member',
            phone='1234567890',
            email='member@example.com',
            age=25,
            national_id='NATIONALID123',
            status='employed (full-time)'
        )

    def test_login_with_email(self):
        """Test that users can log in with email"""
        response = self.client.post('/api/auth/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_login_with_national_id(self):
        """Test that users can log in with national ID"""
        response = self.client.post('/api/auth/login/', {
            'email': 'NATIONALID123',  # Using national_id in email field
            'password': 'testpass123'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_login_with_national_id_spaces_and_case(self):
        """Test that national ID login works with spaces and different case"""
        response = self.client.post('/api/auth/login/', {
            'email': 'nat ion alid 123',  # Spaces and lowercase
            'password': 'testpass123'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """Test that login fails with invalid credentials"""
        response = self.client.post('/api/auth/login/', {
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_national_id_not_found(self):
        """Test that login fails when national ID doesn't exist"""
        response = self.client.post('/api/auth/login/', {
            'email': 'NONEXISTENTID',
            'password': 'testpass123'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_endpoint(self):
        """Test that the /api/auth/me/ endpoint works after login"""
        # First log in
        login_response = self.client.post('/api/auth/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        }, format='json')

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Set authorization header for subsequent requests
        access_token = login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Test the me endpoint
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'test@example.com')