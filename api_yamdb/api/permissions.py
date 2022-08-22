from rest_framework import permissions


class OnlyContributionAdminModeratorOrRead(permissions.BasePermission):
    """Редактировать могут только владелец, админ, модератор."""

    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user == obj.author
                or request.user.is_admin or request.user.is_moderator)


class OnlyAdmin(permissions.BasePermission):
    """Только администратор."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_admin
        return False


class OnlyAdminOrRead(OnlyAdmin):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_admin)
