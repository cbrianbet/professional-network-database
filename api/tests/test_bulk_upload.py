"""TDD tests for the Bulk Member Upload feature."""
import io

import pytest
from django.urls import reverse

from api.models import Member, User
from api.tests.helpers import admin_client, make_csv


pytestmark = pytest.mark.django_db


class TestCSVTemplateEndpoint:
    def test_returns_csv_with_template_download(self, admin_user):
        client = admin_client(admin_user)
        res = client.get(reverse('api:members-csv-template'))
        assert res.status_code == 200
        assert res['Content-Type'] == 'text/csv'
        body = res.content.decode('utf-8')
        assert 'name' in body
        assert 'national_id' in body
        assert 'career' in body
        assert 'status' in body

    def test_unauthenticated_forbidden(self):
        from rest_framework.test import APIClient

        res = APIClient().get(reverse('api:members-csv-template'))
        assert res.status_code in (401, 403)


class TestBulkMemberUploadEndpoint:
    def test_creates_members_from_valid_csv(self, admin_user):
        client = admin_client(admin_user)
        csv_file, _ = make_csv(
            [
                {
                    'name': 'Alice Test',
                    'phone': '0711111111',
                    'email': 'alice@test.com',
                    'age': '29',
                    'national_id': 'AAA111222',
                    'career': 'Analyst',
                    'status': 'employed (full-time)',
                    'country': 'KE',
                },
                {
                    'name': 'Bob Test',
                    'phone': '0722222222',
                    'email': 'bob@test.com',
                    'age': '35',
                    'national_id': 'BBB222333',
                    'career': 'Manager',
                    'status': 'employed (full-time)',
                    'country': 'KE',
                },
            ]
        )
        res = client.post(
            reverse('api:admin-members-bulk-upload'),
            {'file': csv_file},
            format='multipart',
        )
        assert res.status_code == 200
        assert res.data['created'] == 2
        assert res.data['skipped'] == 0
        assert Member.objects.filter(
            national_id__in=['AAA111222', 'BBB222333']
        ).count() == 2

    def test_rejects_missing_required_fields(self, admin_user):
        client = admin_client(admin_user)
        csv_file, _ = make_csv(
            [
                {
                    'name': '',
                    'phone': '071',
                    'email': 'x@t.com',
                    'age': '25',
                    'national_id': 'X1',
                    'career': 'Dev',
                    'status': 'employed (full-time)',
                },
            ]
        )
        res = client.post(
            reverse('api:admin-members-bulk-upload'),
            {'file': csv_file},
            format='multipart',
        )
        assert res.status_code == 200
        assert res.data['created'] == 0
        assert res.data['skipped'] == 1
        assert 'name' in res.data['errors'][0]['error']

    def test_rejects_invalid_status(self, admin_user):
        client = admin_client(admin_user)
        csv_file, _ = make_csv(
            [
                {
                    'name': 'Bad',
                    'phone': '071',
                    'email': 'b@t.com',
                    'age': '25',
                    'national_id': 'BAD1',
                    'career': 'Dev',
                    'status': 'not-a-status',
                },
            ]
        )
        res = client.post(
            reverse('api:admin-members-bulk-upload'),
            {'file': csv_file},
            format='multipart',
        )
        assert res.data['skipped'] == 1
        assert 'status' in res.data['errors'][0]['error']

    def test_dedups_national_id_in_db(self, admin_user, make_member):
        make_member(national_id='DUP001')
        client = admin_client(admin_user)
        csv_file, _ = make_csv(
            [
                {
                    'name': 'Dup',
                    'phone': '071',
                    'email': 'd@t.com',
                    'age': '25',
                    'national_id': 'DUP001',
                    'career': 'Dev',
                    'status': 'employed (full-time)',
                },
            ]
        )
        res = client.post(
            reverse('api:admin-members-bulk-upload'),
            {'file': csv_file},
            format='multipart',
        )
        assert res.data['skipped'] == 1
        assert 'already exists' in res.data['errors'][0]['error']

    def test_dedups_national_id_within_upload(self, admin_user):
        client = admin_client(admin_user)
        csv_file, _ = make_csv(
            [
                {
                    'name': 'A',
                    'phone': '071',
                    'email': 'a@t.com',
                    'age': '25',
                    'national_id': 'SAME1',
                    'career': 'Dev',
                    'status': 'employed (full-time)',
                },
                {
                    'name': 'B',
                    'phone': '072',
                    'email': 'b@t.com',
                    'age': '30',
                    'national_id': 'SAME1',
                    'career': 'Mgr',
                    'status': 'employed (full-time)',
                },
            ]
        )
        res = client.post(
            reverse('api:admin-members-bulk-upload'),
            {'file': csv_file},
            format='multipart',
        )
        assert res.data['created'] == 1
        assert res.data['skipped'] == 1

    def test_rejects_non_csv_file(self, admin_user):
        client = admin_client(admin_user)
        bad = io.BytesIO(b'not a csv')
        bad.name = 'test.txt'
        res = client.post(
            reverse('api:admin-members-bulk-upload'),
            {'file': bad},
            format='multipart',
        )
        assert res.status_code == 400
        assert 'csv' in res.data['error'].lower()

    def test_rejects_no_file(self, admin_user):
        client = admin_client(admin_user)
        res = client.post(
            reverse('api:admin-members-bulk-upload'),
            {},
            format='multipart',
        )
        assert res.status_code == 400

    def test_creates_placeholder_users(self, admin_user):
        client = admin_client(admin_user)
        csv_file, _ = make_csv(
            [
                {
                    'name': 'Place',
                    'phone': '071',
                    'email': 'p@t.com',
                    'age': '25',
                    'national_id': 'PLC001',
                    'career': 'Dev',
                    'status': 'employed (full-time)',
                },
            ]
        )
        res = client.post(
            reverse('api:admin-members-bulk-upload'),
            {'file': csv_file},
            format='multipart',
        )
        assert res.data['created'] == 1
        # Verify a placeholder user was created
        assert User.objects.filter(email__startswith='bulk_').exists()

    def test_non_admin_forbidden(self, regular_user):
        client = admin_client(regular_user)
        csv_file, _ = make_csv(
            [
                {
                    'name': 'Nope',
                    'phone': '071',
                    'email': 'n@t.com',
                    'age': '25',
                    'national_id': 'NOP001',
                    'career': 'Dev',
                    'status': 'employed (full-time)',
                },
            ]
        )
        res = client.post(
            reverse('api:admin-members-bulk-upload'),
            {'file': csv_file},
            format='multipart',
        )
        assert res.status_code == 403
