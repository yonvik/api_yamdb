from rest_framework import viewsets, mixins, filters
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination

from reviews import models as review_models

from . import serializers


class CustomViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    pass


class ReviewViewSet(viewsets.ModelViewSet):
    """Endpoint модели Review."""
    serializer_class = serializers.ReviewSerializer

    def get_queryset(self):
        title = get_object_or_404(
            review_models.Title,
            pk=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        author = self.request.user
        title = get_object_or_404(review_models.Title,
                                  pk=self.kwargs.get('title_id'))
        serializer.save(author=author, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Endpoint модели Comment."""
    serializer_class = serializers.CommentSerializer

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
    queryset = review_models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    # permission_classes = ()
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name', )


class GenreViewSet(CustomViewSet):
    queryset = review_models.Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    # permission_classes = ()
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = review_models.Title.objects.all()
    # permission_classes = ()
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return serializers.TitleCreateSerializer
        return serializers.TitleSerializer
