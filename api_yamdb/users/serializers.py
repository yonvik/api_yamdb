import re

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import USER_ROLE

User = get_user_model()


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
        if self.context['request'].user.role == USER_ROLE:
            return USER_ROLE
        return value
