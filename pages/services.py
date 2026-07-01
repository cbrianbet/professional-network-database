"""Shared business logic extracted from api/views.py."""
from api.models import Member


def get_members_for_user(user):
    """Return members queryset based on user role."""
    if user.role == 'admin':
        return Member.objects.all()
    return Member.objects.filter(user=user)


def compute_kpis(members):
    """Compute KPI counts from a members queryset."""
    return {'total': members.count()}


def compute_chart_data(members):
    """Compute aggregations for dashboard charts."""
    return {}
