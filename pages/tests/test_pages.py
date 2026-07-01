import pytest
from django.test import Client

from api.models import User


@pytest.fixture
def page_client(db):
    return Client()


@pytest.mark.django_db
def test_login_page_renders(page_client):
    res = page_client.get('/login')
    assert res.status_code == 200
    assert b'Member login' in res.content


@pytest.mark.django_db
def test_protected_dashboard_redirects_when_anonymous(page_client):
    res = page_client.get('/dashboard')
    assert res.status_code == 302
    assert res.url.startswith('/login')


@pytest.mark.django_db
def test_session_login_and_jobs_page(admin_user, page_client):
    res = page_client.post('/login', {
        'identifier': admin_user.email,
        'password': 'adminpass123',
    })
    assert res.status_code == 302
    assert res.url == '/dashboard'

    jobs = page_client.get('/jobs')
    assert jobs.status_code == 200
    assert b'Job Opportunities' in jobs.content
    assert b'id="shared-shell"' not in jobs.content


@pytest.mark.django_db
def test_logout_clears_session(admin_user, page_client):
    page_client.post('/login', {'identifier': admin_user.email, 'password': 'adminpass123'})
    res = page_client.post('/logout')
    assert res.status_code == 302
    assert page_client.get('/dashboard').status_code == 302
