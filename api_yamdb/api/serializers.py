from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

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


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = review_models.Comment
        fields = (
            'id',
            'text',
            'author',
            'pub_date'
        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = review_models.Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = review_models.Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = review_models.Title
        fields = (
            'id', 'name', 'category', 'genre',
            'year', 'description',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=review_models.Title.objects.all(),
                fields=('name', 'year'),
                message='Данное произведение существует'
            )
        ]


class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(slug_field='slug',
                                         queryset=review_models.Genre.objects.all(),
                                         many=True)
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=review_models.Category.objects.all())

    class Meta:
        model = review_models.Title
        fields = '__all__'
