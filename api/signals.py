"""
Signal handlers for the professional network application.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User
from .notifications import send_approval_notification, send_rejection_notification

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def user_status_change_handler(sender, instance, created, **kwargs):
    """
    Handle user status changes - send notifications when a pending user is approved or rejected.
    """
    # Only process if this is not a newly created user (we don't want to notify on signup)
    if not created:
        # Get the current instance from DB to compare with previous state
        try:
            old_instance = User.objects.get(pk=instance.pk)
            # Check if status changed from pending to active/disabled
            if old_instance.status == 'pending' and instance.status in ['active', 'disabled']:
                if instance.status == 'active':
                    # User was approved
                    send_approval_notification(instance)
                    logger.info(f"Approval notification sent for user {instance.email}")
                elif instance.status == 'disabled':
                    # User was rejected/disabled
                    send_rejection_notification(instance)
                    logger.info(f"Rejection notification sent for user {instance.email}")
        except User.DoesNotExist:
            # This shouldn't happen, but handle gracefully
            pass
        except Exception as e:
            # Log error but don't break the save operation
            logger.error(f"Error in user status change handler: {str(e)}")
