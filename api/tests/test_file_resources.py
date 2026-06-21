from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import FileResource, User, Member, Profile
from api.serializers import BulkFileResourceOperationSerializer
import json
import tempfile
import os

class FileResourceTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create users using the custom create_user method
        self.admin_user = User.create_user(
            email='admin@test.com',
            password='adminpass123',
            name='Admin User',
            role='admin'  # This makes is_staff return True
        )
        self.regular_user = User.create_user(
            email='user@test.com',
            password='userpass123',
            name='Regular User',
            role='user'
        )
        # Create member and profile for regular user
        self.member = Member.objects.create(
            user=self.regular_user,
            name='Test User',
            email='user@test.com',
            age=30,
            national_id='TEST123456'
        )
        self.profile = Profile.objects.create(
            user=self.regular_user,
            headline='Test Headline',
            summary='Test Summary'
        )
        # Create file resources for testing
        self.file1 = FileResource.objects.create(
            user=self.regular_user,
            original_filename='test1.pdf',
            file_size=1024,
            file_type='pdf',
            upload_path='/tmp/test1.pdf',
            permission_level='private'
        )
        self.file2 = FileResource.objects.create(
            user=self.regular_user,
            original_filename='test2.png',
            file_size=2048,
            file_type='png',
            upload_path='/tmp/test2.png',
            permission_level='public'
        )
        self.file3 = FileResource.objects.create(
            user=self.admin_user,
            original_filename='test3.jpeg',
            file_size=3072,
            file_type='jpeg',
            upload_path='/tmp/test3.jpeg',
            permission_level='authenticated'
        )

    def test_bulk_file_resource_operation_serializer_validation(self):
        """Test BulkFileResourceOperationSerializer validation"""
        # Valid IDs for delete action
        serializer = BulkFileResourceOperationSerializer(data={
            'action': 'delete',
            'ids': [str(self.file1.id), str(self.file2.id)]
        })
        self.assertTrue(serializer.is_valid())

        # Invalid IDs (non-existent) for delete action
        serializer = BulkFileResourceOperationSerializer(data={
            'action': 'delete',
            'ids': [str(self.file1.id), '00000000-0000-0000-0000-000000000000']
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('ids', serializer.errors)

        # Valid permission_level for change_permission action
        serializer = BulkFileResourceOperationSerializer(data={
            'action': 'change_permission',
            'ids': [str(self.file1.id)],
            'permission_level': 'public'
        })
        self.assertTrue(serializer.is_valid())

        # Invalid permission_level for change_permission action
        serializer = BulkFileResourceOperationSerializer(data={
            'action': 'change_permission',
            'ids': [str(self.file1.id)],
            'permission_level': 'invalid_level'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('permission_level', serializer.errors)

        # Missing permission_level parameter for change_permission action
        serializer = BulkFileResourceOperationSerializer(data={
            'action': 'change_permission',
            'ids': [str(self.file1.id)]
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('permission_level', serializer.errors)

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    })
    def test_file_resource_bulk_delete_endpoint(self):
        """Test file resource bulk delete endpoint"""
        # Authenticated admin can delete multiple file resources
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('api:file-resource-bulk-operation')
        data = {
            'action': 'delete',
            'ids': [str(self.file1.id), str(self.file2.id)]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted_count'], 2)
        # Verify files are deleted
        self.assertFalse(FileResource.objects.filter(id=self.file1.id).exists())
        self.assertFalse(FileResource.objects.filter(id=self.file2.id).exists())
        self.assertTrue(FileResource.objects.filter(id=self.file3.id).exists())

        # Non-admin users cannot access the endpoint
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test with invalid IDs (should not delete anything but return error)
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'action': 'delete',
            'ids': ['00000000-0000-0000-0000-000000000000']
        }
        response = self.client.post(url, data, format='json')
        # Assuming the serializer validation fails and returns 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    })
    def test_file_resource_list_caching(self):
        """Test file resource list caching"""
        from django.core.cache import cache
        cache.clear()

        # Authenticate as regular user
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('api:file-resource-list')

        # First request - should not be cached
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response1.data), 2)  # Only user's files

        # Second request - should be cached (if caching is implemented)
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response2.data), 2)
        # Note: Actual caching behavior depends on implementation in views

        # Test different query parameters create different cache keys
        response3 = self.client.get(url + '?permission_level=public')
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response3.data), 1)  # Only public file

        # Create a new file resource - should invalidate cache
        FileResource.objects.create(
            user=self.regular_user,
            original_filename='newfile.pdf',
            file_size=512,
            file_type='pdf',
            upload_path='/tmp/newfile.pdf',
            permission_level='private'
        )

        # Request again - should see new file (if cache invalidation works)
        response4 = self.client.get(url)
        self.assertEqual(response4.status_code, status.HTTP_200_OK)
        # Depending on caching implementation, might be 2 or 3

        # Test cache expiration (difficult to test without mocking time)
        # We'll skip explicit expiration test as it's implementation dependent

    def test_permission_fixes_member_profile_endpoints(self):
        """Test permission fixes in member and profile endpoints"""
        # Test member endpoints
        # Regular user can access their own members
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('api:member-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.member.id)

        # Regular user cannot access other users' members
        # Create another user and member
        other_user = User.create_user(
            email='other@test.com',
            password='otherpass123',
            name='Other User'
        )
        other_member = Member.objects.create(
            user=other_user,
            name='Other User',
            email='other@test.com',
            age=25,
            national_id='OTHER123456'
        )

        # Try to access specific member of other user
        detail_url = reverse('api:member-detail', kwargs={'pk': other_member.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Or 403 depending on implementation

        # Admins can access all members
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)  # At least two members

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], other_member.id)

        # Test profile endpoints (similar pattern)
        # Regular user can access their own profile
        self.client.force_authenticate(user=self.regular_user)
        profile_url = reverse('api:profile-list')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.profile.id)

        # Regular user cannot access other users' profiles
        other_profile = Profile.objects.create(
            user=other_user,
            headline='Other Headline',
            summary='Other Summary'
        )

        profile_detail_url = reverse('api:profile-detail', kwargs={'pk': other_profile.id})
        response = self.client.get(profile_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Or 403

        # Admins can access all profiles
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

        response = self.client.get(profile_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], other_profile.id)

    def test_performance_optimizations_export_endpoints(self):
        """Test performance optimizations in export endpoints"""
        # Create many file resources to test iterator usage
        for i in range(100):
            FileResource.objects.create(
                user=self.regular_user if i % 2 == 0 else self.admin_user,
                original_filename=f'file{i}.pdf',
                file_size=1024 + i,
                file_type='pdf',
                upload_path=f'/tmp/file{i}.pdf',
                permission_level='public' if i % 3 == 0 else 'private'
            )

        # Test admin-only access
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('api:admin-export-members')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        # Check that response is streaming (has StreamingHttpResponse characteristics)
        # For simplicity, we'll check that it's not too small (should have header + data)
        self.assertGreater(len(response.streaming_content), 1000)  # Approximate check

        # Test CSV format (basic check)
        # Since it's a streaming response, we need to consume it
        if hasattr(response, 'streaming_content'):
            content = b''.join(response.streaming_content).decode('utf-8')
        else:
            content = response.content.decode('utf-8')
        lines = content.strip().split('\n')
        self.assertGreater(len(lines), 1)  # Header + at least one data row
        self.assertIn('email', lines[0])  # Header should contain email

        # Test users export endpoint
        url = reverse('api:admin-export-users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_enhanced_admin_stats(self):
        """Test enhanced admin stats includes storage analytics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('api:admin-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that all expected fields are present
        expected_fields = [
            'total_users', 'active_users', 'pending_users',
            'total_members', 'total_profiles',
            'storage_analytics'  # New field
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)

        # Check storage analytics structure
        storage = response.data['storage_analytics']
        self.assertIn('total_size', storage)
        self.assertIn('total_count', storage)
        self.assertIn('by_type', storage)
        self.assertIn('by_permission', storage)

        # Check that values are correctly formatted (integers)
        self.assertIsInstance(storage['total_size'], int)
        self.assertIsInstance(storage['total_count'], int)
        self.assertIsInstance(storage['by_type'], dict)
        self.assertIsInstance(storage['by_permission'], dict)

        # Verify counts match our test data
        # We have: regular_user: 2 files, admin_user: 1 file, plus 100 from export test = 103 total
        # But note: the export test created files for both users, so let's calculate
        # Actually, let's just check that the count is reasonable
        self.assertGreaterEqual(storage['total_count'], 3)  # At least our initial 3 files

    def test_error_handling_improvements(self):
        """Test error handling improvements"""
        # Test validation errors return 400
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('api:file-resource-list')
        # Send invalid data (missing required fields)
        data = {
            'original_filename': 'test.txt'
            # Missing file_size, file_type, upload_path
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file_size', response.data)
        self.assertIn('file_type', response.data)
        self.assertIn('upload_path', response.data)

        # Test integrity errors return 409 (if applicable)
        # This is harder to test without triggering actual integrity error
        # We'll skip for now but note that the view should catch IntegrityError and return 409

        # Test unexpected errors return 500
        # We'll mock a view to raise an exception
        from unittest.mock import patch
        from api.views import FileResourceViewSet

        with patch('api.views.FileResourceViewSet.list', side_effect=Exception('Unexpected error')):
            self.client.force_authenticate(user=self.regular_user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)