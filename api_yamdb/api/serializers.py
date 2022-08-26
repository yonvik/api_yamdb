import re

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from reviews import models as review_models
from reviews.validators import validate_title_year

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault())
    title = serializers.HiddenField(default=None)

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
        validators = [
            UniqueTogetherValidator(
                queryset=review_models.Review.objects.all(),
                fields=('title', 'author'),
            )
        ]


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
        return validate_title_year(value)


class UsernameField(serializers.Field):
    NOT_ALLOWED_USERNAMES = ['me']
    ERROR_REGEX_MESSAGE = ('username может состоять только из букв, '
                           'цифр и спецсимволов: @.+-_')

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if data in self.NOT_ALLOWED_USERNAMES:
            raise serializers.ValidationError(
                'Поле username не может содержать значение: ', data
            )
        if re.search(r'^[\w.@+-]+\Z', data) is None:
            raise serializers.ValidationError(self.ERROR_REGEX_MESSAGE)
        if User.objects.filter(username=data).exists():
            raise serializers.ValidationError(
                "A user with this username already exists!")
        return data


class RegistrationSerializer(serializers.Serializer):
    """ Сериализация регистрации пользователя и создания нового. """
    username = UsernameField()
    email = serializers.EmailField()


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    username = UsernameField()

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'bio', 'role'
        )

    def validate_role(self, value):
        if self.context['request'].user.role == review_models.USER_ROLE:
            return review_models.USER_ROLE
        return value
