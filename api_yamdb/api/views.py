from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from reviews import models as review_models

from . import serializers


class ReviewViewSet(viewsets.ModelViewSet):
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
