from rest_framework import permissions

from users.models import MODERATOR_ROLE, ADMIN_ROLE


class OnlyContributionAdminModeratorOrRead(permissions.BasePermission):
    """Редактировать могут только владелец, админ, модератор."""

    ALLOW_EDIT_ROLE = [
        MODERATOR_ROLE,
        ADMIN_ROLE
    ]

    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user == obj.author
                or request.user.role in self.ALLOW_EDIT_ROLE)


class OnlyAdmin(permissions.BasePermission):
    """Только администратор."""
    ALLOW_ROLE = ADMIN_ROLE

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == self.ALLOW_ROLE
        return False


class OnlyAdminOrRead(OnlyAdmin):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.role == self.ALLOW_ROLE)
