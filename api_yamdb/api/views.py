import django_filters
from django.db import IntegrityError
from django.db.models import Avg
from rest_framework import viewsets, mixins, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from reviews import models as review_models

from . import serializers
from . import permissions
from . import paginators


class CustomViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    pass


class ReviewViewSet(viewsets.ModelViewSet):
    """Endpoint модели Review."""
    serializer_class = serializers.ReviewSerializer
    permission_classes = (
        permissions.OnlyContributionAdminModeratorOrRead,)
    pagination_class = paginators.StandardResultsSetPagination

    def get_queryset(self):
        title = get_object_or_404(
            review_models.Title,
            pk=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, args, kwargs)
        except IntegrityError:
            return Response('Можно сотавить только 1 отзыв.',
                            status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        author = self.request.user
        title = get_object_or_404(review_models.Title,
                                  pk=self.kwargs.get('title_id'))
        serializer.save(author=author, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Endpoint модели Comment."""
    serializer_class = serializers.CommentSerializer
    permission_classes = (
        permissions.OnlyContributionAdminModeratorOrRead,)
    pagination_class = paginators.StandardResultsSetPagination

    def get_queryset(self):
        review = get_object_or_404(review_models.Review,
                                   pk=self.kwargs['review_id'],
                                   title__pk=self.kwargs['title_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        author = self.request.user
        review = get_object_or_404(review_models.Review,
                                   pk=self.kwargs['review_id'],
                                   title__pk=self.kwargs['title_id'])
        serializer.save(author=author, review=review)


class CategoryViewSet(CustomViewSet):
    """Endpoint модели Category."""
    queryset = review_models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = (permissions.OnlyAdminOrRead,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    pagination_class = paginators.StandardResultsSetPagination


class GenreViewSet(CustomViewSet):
    """Endpoint модели Genre."""
    queryset = review_models.Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    permission_classes = (permissions.OnlyAdminOrRead,)
    lookup_field = 'slug'
    pagination_class = paginators.StandardResultsSetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)


class TitleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='contains'
    )
    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact'
    )
    genre = django_filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='exact'
    )

    class Meta:
        model = review_models.Title
        fields = ['name', 'category', 'genre', 'year']


class TitleViewSet(viewsets.ModelViewSet):
    """Endpoint модели Title."""
    queryset = review_models.Title.objects.annotate(
        rating=Avg('reviews__score'))
    permission_classes = (permissions.OnlyAdminOrRead,)
    pagination_class = paginators.StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return serializers.TitleCreateSerializer
        return serializers.TitleSerializer
