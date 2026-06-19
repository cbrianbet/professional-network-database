#!/usr/bin/env python3
"""
QA Test Script for Sprint 2 Features
Tests the new functionality implemented in Sprint 2
"""

import os
import sys
import django
import time

def get_unique_email(base_name):
    """Generate a unique email address to avoid conflicts"""
    timestamp = int(time.time() * 1000)  # milliseconds since epoch
    return f"{base_name}_{timestamp}@example.com"

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.append('/Users/charlesbett/Source/professional-network-database')

django.setup()

from api.models import User, Member, FileResource
from api.serializers import SignupSerializer
from rest_framework.test import APIClient
from rest_framework import status
import tempfile

def test_file_resource_model():
    """Test FileResource model with new fields"""
    print("Testing FileResource model...")

    # Create a user to associate with the file resource
    user = User.create_user(
        email=get_unique_email('fileresource_test'),
        password='testpass123',
        name='Test User'
    )

    # Create a FileResource instance
    file_resource = FileResource.objects.create(
        user=user,
        original_filename='test.pdf',
        file_size=1024,
        file_type='pdf',
        upload_path='/tmp/test.pdf',
        permission_level='public'
    )

    # Test that the fields exist and have correct values
    assert file_resource.original_filename == 'test.pdf'
    assert file_resource.file_size == 1024
    assert file_resource.file_type == 'pdf'
    assert file_resource.upload_path == '/tmp/test.pdf'
    assert file_resource.permission_level == 'public'
    assert file_resource.thumbnail_path == ''  # Default blank

    # Test permission level choices
    file_resource.permission_level = 'private'
    file_resource.save()
    assert file_resource.permission_level == 'private'

    file_resource.permission_level = 'authenticated'
    file_resource.save()
    assert file_resource.permission_level == 'authenticated'

    print("✓ FileResource model tests passed")
    return True

def test_pending_user_status():
    """Test that new users start with pending status"""
    print("Testing pending user status...")

    # Test SignupSerializer sets status to pending
    serializer_data = {
        'name': 'New User',
        'email': get_unique_email('pendingtest'),
        'password': 'securepass123'
    }
    serializer = SignupSerializer(data=serializer_data)
    print(f"Serializer data: {serializer_data}")
    print(f"Serializer is_valid: {serializer.is_valid()}")
    if not serializer.is_valid():
        print(f"Serializer errors: {serializer.errors}")
    assert serializer.is_valid()

    user = serializer.save()
    print(f"Created user: {user.email}, status: {user.status}")
    assert user.status == 'pending'
    assert user.email == serializer_data['email']  # Use the generated email
    assert user.name == 'New User'

    print("✓ Pending user status tests passed")
    return True

def test_login_blocks_pending_users():
    """Test that login is blocked for pending users"""
    print("Testing login blocking for pending users...")

    client = APIClient()

    # Create a pending user
    pending_email = get_unique_email('loginpending')
    user = User.create_user(
        email=pending_email,
        password='testpass123',
        name='Pending User',
        status='pending'
    )

    # Try to login - should fail with pending status error
    response = client.post('/api/auth/login/', {
        'email': pending_email,
        'password': 'testpass123'
    }, format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'pending' in response.data['error'].lower()

    # Now activate the user and try again - should succeed
    user.status = 'active'
    user.save()

    response = client.post('/api/auth/login/', {
        'email': pending_email,
        'password': 'testpass123'
    }, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert 'token' in response.data

    print("✓ Login blocking for pending users tests passed")
    return True

def test_admin_user_management_enhancements():
    """Test enhanced admin user management views"""
    print("Testing admin user management enhancements...")

    client = APIClient()

    # Create an admin user
    admin_email = get_unique_email('adminmgmt')
    admin_user = User.create_user(
        email=admin_email,
        password='adminpass123',
        name='Admin User',
        role='admin',
        status='active'
    )

    # Login as admin
    login_response = client.post('/api/auth/login/', {
        'email': admin_email,
        'password': 'adminpass123'
    }, format='json')
    print(f"Login response status: {login_response.status_code}")
    if login_response.status_code != status.HTTP_200_OK:
        print(f"Login response data: {login_response.data}")
    assert login_response.status_code == status.HTTP_200_OK
    access_token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Create a regular user to manage
    regular_email = get_unique_email('regularmgmt')
    regular_user = User.create_user(
        email=regular_email,
        password='regularpass123',
        name='Regular User',
        status='pending'
    )

    # Test GET admin/users/<id>/
    url = f'/api/admin/users/{regular_user.id}/'
    print(f"Calling GET URL: {url}")
    response = client.get(url)
    print(f"GET user response status: {response.status_code}")
    print(f"GET user response content: {response.content}")
    if hasattr(response, 'data'):
        print(f"GET user response data: {response.data}")
    if response.status_code != status.HTTP_200_OK:
        print(f"GET user response error: {response.content}")
    assert response.status_code == status.HTTP_200_OK
    assert response.data['user']['email'] == regular_email
    assert response.data['user']['status'] == 'pending'

    # Test PATCH admin/users/<id>/ to activate user
    response = client.patch(f'/api/admin/users/{regular_user.id}/', {
        'status': 'active'
    }, format='json')
    print(f"PATCH user response status: {response.status_code}")
    if response.status_code != status.HTTP_200_OK:
        print(f"PATCH user response data: {response.data}")
    assert response.status_code == status.HTTP_200_OK
    assert response.data['user']['status'] == 'active'

    # Verify the user was actually updated
    regular_user.refresh_from_db()
    assert regular_user.status == 'active'

    # Test DELETE admin/users/<id>/
    response = client.delete(f'/api/admin/users/{regular_user.id}/')
    print(f"DELETE user response status: {response.status_code}")
    if response.status_code != status.HTTP_200_OK:
        print(f"DELETE user response data: {response.data}")
    assert response.status_code == status.HTTP_200_OK
    assert response.data['success'] == True

    # Verify user was deleted
    assert not User.objects.filter(id=regular_user.id).exists()

    # Test GET admin/users/ with status filter
    user1_email = get_unique_email('user1mgmt')
    user2_email = get_unique_email('user2mgmt')
    user1 = User.create_user(
        email=user1_email,
        password='pass123',
        name='User 1',
        status='active'
    )
    user2 = User.create_user(
        email=user2_email,
        password='pass123',
        name='User 2',
        status='pending'
    )

    # Filter by active status
    response = client.get('/api/admin/users/?status=active')
    print(f"GET users (active) response status: {response.status_code}")
    if response.status_code != status.HTTP_200_OK:
        print(f"GET users (active) response data: {response.data}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['users']) >= 1  # At least our active user

    # Filter by pending status
    response = client.get('/api/admin/users/?status=pending')
    print(f"GET users (pending) response status: {response.status_code}")
    if response.status_code != status.HTTP_200_OK:
        print(f"GET users (pending) response data: {response.data}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['users']) >= 1  # At least our pending user

    print("✓ Admin user management enhancements tests passed")
    return True

def test_admin_stats_endpoint():
    """Test admin stats endpoint"""
    print("Testing admin stats endpoint...")

    client = APIClient()

    # Create an admin user
    admin_email = get_unique_email('adminstats')
    admin_user = User.create_user(
        email=admin_email,
        password='adminpass123',
        name='Admin User',
        role='admin',
        status='active'
    )

    # Login as admin
    login_response = client.post('/api/auth/login/', {
        'email': admin_email,
        'password': 'adminpass123'
    }, format='json')

    assert login_response.status_code == status.HTTP_200_OK
    access_token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Create some test users
    user1_email = get_unique_email('user1stats')
    user2_email = get_unique_email('user2stats')
    user3_email = get_unique_email('user3stats')
    User.create_user(
        email=user1_email,
        password='pass123',
        name='User 1',
        role='user',
        status='active'
    )
    User.create_user(
        email=user2_email,
        password='pass123',
        name='User 2',
        role='user',
        status='pending'
    )
    User.create_user(
        email=user3_email,
        password='pass123',
        name='User 3',
        role='admin',
        status='active'
    )

    # Test the stats endpoint
    response = client.get('/api/admin/stats/')
    assert response.status_code == status.HTTP_200_OK

    # Check that we have the expected data structure
    assert 'total_users' in response.data
    assert 'users_by_role' in response.data
    assert 'users_by_status' in response.data
    assert 'recent_users' in response.data

    # Check specific values
    assert response.data['total_users'] >= 3  # At least the 3 we created
    assert response.data['users_by_role']['user'] >= 2  # At least 2 regular users
    assert response.data['users_by_role']['admin'] >= 2  # At least 2 admins
    assert response.data['users_by_status']['active'] >= 2  # At least 2 active
    assert response.data['users_by_status']['pending'] >= 1  # At least 1 pending

    print("✓ Admin stats endpoint tests passed")
    return True

def test_admin_user_approve_reject():
    """Test admin user approve/reject endpoint"""
    print("Testing admin user approve/reject endpoint...")

    client = APIClient()

    # Create an admin user
    admin_email = get_unique_email('adminapprove')
    admin_user = User.create_user(
        email=admin_email,
        password='adminpass123',
        name='Admin User',
        role='admin',
        status='active'
    )

    # Login as admin
    login_response = client.post('/api/auth/login/', {
        'email': admin_email,
        'password': 'adminpass123'
    }, format='json')

    assert login_response.status_code == status.HTTP_200_OK
    access_token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Create a pending user
    pending_email = get_unique_email('pendingapprove')
    pending_user = User.create_user(
        email=pending_email,
        password='pass123',
        name='Pending User',
        status='pending'
    )

    # Test approving the user
    response = client.patch(f'/api/admin/users/{pending_user.id}/approve-reject/', {
        'status': 'active'
    }, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['user']['status'] == 'active'

    # Verify the user was actually updated
    pending_user.refresh_from_db()
    assert pending_user.status == 'active'

    # Create another pending user to test rejection
    pending2_email = get_unique_email('pending2approve')
    pending_user2 = User.create_user(
        email=pending2_email,
        password='pass123',
        name='Pending User 2',
        status='pending'
    )

    # Test rejecting the user
    response = client.patch(f'/api/admin/users/{pending_user2.id}/approve-reject/', {
        'status': 'disabled'
    }, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['user']['status'] == 'disabled'

    # Verify the user was actually updated
    pending_user2.refresh_from_db()
    assert pending_user2.status == 'disabled'

    # Test trying to approve/reject a non-pending user (should fail)
    active_email = get_unique_email('activeapprove')
    active_user = User.create_user(
        email=active_email,
        password='pass123',
        name='Active User',
        status='active'
    )

    response = client.patch(f'/api/admin/users/{active_user.id}/approve-reject/', {
        'status': 'disabled'
    }, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'pending' in response.data['error'].lower()

    # Test invalid status
    # Test invalid status
    invalid_user_email = get_unique_email('invaliduser')
    invalid_user = User.create_user(
        email=invalid_user_email,
        password='pass123',
        name='Invalid User',
        status='pending'
    )
    response = client.patch(f'/api/admin/users/{invalid_user.id}/approve-reject/', {
        'status': 'invalid_status'
    }, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'active' in response.data['error'] and 'disabled' in response.data['error']


    print("✓ Admin user approve/reject tests passed")
    return True

def run_all_tests():
    """Run all Sprint 2 QA tests"""
    print("=" * 60)
    print("SPRINT 2 QA TESTING")
    print("=" * 60)

    tests = [
        test_file_resource_model,
        test_pending_user_status,
        test_login_blocks_pending_users,
        test_admin_user_management_enhancements,
        test_admin_stats_endpoint,
        test_admin_user_approve_reject
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} failed with exception: {e}")

    print("=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("🎉 ALL SPRINT 2 QA TESTS PASSED!")
        return True
    else:
        print(f"❌ {failed} test(s) failed")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)