from rest_framework import permissions


class AllowEditOrReadOnly(permissions.BasePermission):
    """Редактировать могут только владелец, админ, модератор."""

    ALLOW_EDIT_ROLE = [
        'moderator',
        'admin'
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
    ALLOW_ROLE = 'admin'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == self.ALLOW_ROLE


class OnlyAdminOrRead(OnlyAdmin):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.role == self.ALLOW_ROLE)
