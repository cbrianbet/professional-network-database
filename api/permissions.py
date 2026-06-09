from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """Allow access only to users with role == 'admin'."""

    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, 'role', None) == 'admin')
