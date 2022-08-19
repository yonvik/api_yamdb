from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Предоставление категории пользователей в админке."""
    list_display = ('id', 'username', 'email', 'password')
