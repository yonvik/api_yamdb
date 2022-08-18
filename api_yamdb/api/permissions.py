from rest_framework import permissions


class ContributionOrModeratorOrAdmin(permissions.BasePermission):
    ALLOW_ROLE = [
        'user',
        'moderator',
        'admin'
    ]

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.role in self.ALLOW_ROLE
        return False

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author
