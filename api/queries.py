from datetime import timedelta

from django.db import models
from django.utils import timezone

from .models import JobAdvert


def visible_job_adverts():
    """Job adverts visible on the public jobs page."""
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    return JobAdvert.objects.select_related('file', 'created_by').filter(
        models.Q(deadline__gte=today)
        | models.Q(deadline__isnull=True, created_at__date__gte=thirty_days_ago)
    )
