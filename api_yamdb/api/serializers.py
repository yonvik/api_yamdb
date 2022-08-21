from django.db import IntegrityError
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import APIException
from rest_framework.validators import UniqueTogetherValidator

from reviews import models as review_models


class UniqueConstraintValidation(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault())
    title = serializers.HiddenField(
        default=None
    )

    class Meta:
        model = review_models.Review
        fields = (
            'id',
            'text',
            'author',
            'title',
            'score',
            'pub_date'
        )

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise UniqueConstraintValidation()


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
    rating = serializers.IntegerField()

    class Meta:
        model = review_models.Title
        fields = ('id', 'name', 'category', 'genre',
                  'year', 'description', 'rating',
                  )
        extra_kwargs = {
            'name': {'read_only': True},
            'category': {'read_only': True},
            'genre': {'read_only': True},
            'year': {'read_only': True},
            'description': {'read_only': True},
            'rating': {'read_only': True},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=review_models.Title.objects.all(),
                fields=('name', 'year'),
                message='Данное произведение существует'
            )
        ]


class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=review_models.Genre.objects.all(),
        many=True)
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=review_models.Category.objects.all())

    class Meta:
        model = review_models.Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category',)

    def validate_year(self, value):
        year = timezone.datetime.now().year
        if value > year:
            raise serializers.ValidationError(
                f'Год выпуска больше {year}'
            )
        return value
