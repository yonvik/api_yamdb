from collections import OrderedDict
from dataclasses import field

from rest_framework import serializers, status
from django.contrib.auth import get_user_model

from . import exceptions

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    """ Сериализация регистрации пользователя и создания нового. """
    NOT_ALLOWED_USERNAMES = ['me']
    username = serializers.CharField()
    email = serializers.EmailField(allow_blank=False)


    def validate_username(self, value):
        if value in self.NOT_ALLOWED_USERNAMES:
            raise serializers.ValidationError(
                'Поле username не может содержать значение: ', value
            )
        return value


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, required=True)
    confirmation_code = serializers.CharField(max_length=256, required=True)

    class Meta:
        model = User
        fields = '__all__'

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise exceptions.CustomValidation(
                'user does not exist',
                status_code=status.HTTP_404_NOT_FOUND
            )
        return value



def username_not_me(username):
    if username == 'me':
        raise serializers.ValidationError('использовать имя "me" запрещено!')
    return username


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'bio', 'role'
        )

    def validate_username(self, username):
        return username_not_me(username)


class UserInfoSerializer(RegistrationSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'bio', 'role'
        )
