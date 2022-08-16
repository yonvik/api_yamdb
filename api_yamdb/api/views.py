from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from reviews import models as review_models

from . import serializers


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

