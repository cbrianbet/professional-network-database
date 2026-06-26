"""Shared test utilities for the API test suite."""
import csv
import io

from rest_framework.test import APIClient


def auth_client(user):
    """Return an APIClient authenticated as the given user."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def admin_client(admin_user):
    """Return an admin-authenticated APIClient."""
    return auth_client(admin_user)


def make_csv(rows, header=None):
    """Build an in-memory CSV file for upload tests.

    rows: list of dicts.
    header: optional column order. Defaults to keys of first row.
    Returns (BytesIO, columns).
    """
    if not rows:
        return io.BytesIO(b''), []
    columns = header or list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
    f = io.BytesIO(buf.getvalue().encode('utf-8'))
    f.name = 'members.csv'
    return f, columns
