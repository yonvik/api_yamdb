from reviews.validators import validate_year_title
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews import models as review_models
from reviews.validators import username_validator


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault())
    title = serializers.HiddenField(default=review_models.Title.objects.all())

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

    def validate(self, attrs):
        author = self.context['request'].user
        request_method = self.context['request'].method
        title_id = self.context['view'].kwargs.get('title_id')
        if request_method == 'POST' and review_models.Review.objects.filter(
                author=author,
                title__pk=title_id).exists():
            raise serializers.ValidationError('Можно оставить только 1 отзыв.')
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


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    username = serializers.CharField(
        max_length=review_models.MAX_LENGTH_USERNAME,
        validators=[
            UniqueValidator(queryset=review_models.User.objects.all()),
            username_validator
        ]
    )

    class Meta:
        model = review_models.User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'bio', 'role'
        )
