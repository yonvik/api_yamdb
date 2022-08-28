from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from reviews import models as review_models
from reviews.validators import username_validator, validate_year_title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault())
    score = serializers.IntegerField(validators=[
        MaxValueValidator(
            limit_value=review_models.MAXIMUM_SCORE,
            message=f'Оценка не может быть больше {review_models.MAXIMUM_SCORE}'),
        MinValueValidator(
            limit_value=review_models.MINIMAL_SCORE,
            message=f'Оценка не может быть меньше {review_models.MINIMAL_SCORE}'
        )
    ])

    class Meta:
        model = review_models.Review
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date'
        )

    def validate(self, attrs):
        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            title = get_object_or_404(review_models.Title, pk=title_id)
            if title.reviews.filter(
                    author=self.context['request'].user).exists():
                raise serializers.ValidationError(
                    'Можно оставить только 1 отзыв.')
        return attrs


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

        read_only_fields = ('__all__',)


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
        return validate_year_title(value)


class RegistrationSerializer(serializers.Serializer):
    """ Сериализация регистрации пользователя и создания нового. """
    username = serializers.CharField(
        max_length=review_models.MAX_LENGTH_USERNAME,
        validators=[username_validator]
    )
    email = serializers.EmailField(max_length=review_models.MAX_LENGTH_EMAIL)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=review_models.MAX_LENGTH_USERNAME,
        validators=[username_validator]
    )
    confirmation_code = serializers.CharField(
        max_length=review_models.MAX_LENGTH_CONFIRMATION_CODE
    )


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""

    class Meta:
        model = review_models.User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'bio', 'role'
        )

    def validate_username(self, value):
        return username_validator(value)
