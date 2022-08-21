from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Предоставление категории комментариев в админке."""
    list_display = ('id', 'text', 'author', 'review')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Предоставление категорий в админке."""
    list_display = ('id', 'name', 'slug')


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Предоставление категории жанров в админке."""
    list_display = ('id', 'name', 'year', 'category')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Предоставление категории ревью в админке."""
    list_display = ('id', 'text', 'score', 'author', 'title')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Предоставление категории жанров в админке."""
    list_display = ('id', 'name', 'slug')
