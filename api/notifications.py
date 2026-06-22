"""
Notification service for sending email notifications.
"""
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
import threading

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications asynchronously."""
    
    @staticmethod
    def send_approval_email(user, login_url=None):
        """Send account approval email to user."""
        try:
            subject = "Your Account Has Been Approved - Professional Network"
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@professionalnetwork.com')
            to_email = user.email
            
            context = {
                'user': user,
                'login_url': login_url or f"{getattr(settings, 'FRONTEND_URL', '')}/login.html",
                'current_year': 2026
            }
            
            html_content = render_to_string('email/user_approved.html', context)
            text_content = strip_tags(html_content)
            
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            
            # Send email in background thread to avoid blocking API response
            thread = threading.Thread(target=NotificationService._send_email, args=(msg,))
            thread.daemon = True
            thread.start()
            
            logger.info(f"Approval email queued for user {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to queue approval email for user {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_rejection_email(user, rejection_reason=None, support_url=None):
        """Send account rejection email to user."""
        try:
            subject = "Account Update Required - Professional Network"
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@professionalnetwork.com')
            to_email = user.email
            
            context = {
                'user': user,
                'rejection_reason': rejection_reason,
                'support_url': support_url or f"{getattr(settings, 'FRONTEND_URL', '')}/support.html",
                'current_year': 2026
            }
            
            html_content = render_to_string('email/user_rejected.html', context)
            text_content = strip_tags(html_content)
            
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            
            # Send email in background thread to avoid blocking API response
            thread = threading.Thread(target=NotificationService._send_email, args=(msg,))
            thread.daemon = True
            thread.start()
            
            logger.info(f"Rejection email queued for user {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to queue rejection email for user {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def _send_email(msg):
        """Actually send the email (called in background thread)."""
        try:
            msg.send()
            logger.info(f"Email sent successfully to {msg.to}")
        except Exception as e:
            logger.error(f"Failed to send email to {msg.to}: {str(e)}")

def send_approval_notification(user, login_url=None):
    """Convenience function to send approval notification."""
    return NotificationService.send_approval_email(user, login_url)

def send_rejection_notification(user, rejection_reason=None, support_url=None):
    """Convenience function to send rejection notification."""
    return NotificationService.send_rejection_email(user, rejection_reason, support_url)
