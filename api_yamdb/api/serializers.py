from rest_framework import serializers

from reviews import models as review_models


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username')

    class Meta:
        model = review_models.Review
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date'
        )
