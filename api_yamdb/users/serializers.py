import re
from collections import OrderedDict
from dataclasses import field, fields
from enum import unique
from queue import Empty

from django.contrib.auth import get_user_model
from rest_framework import serializers, status

from . import exceptions
from .models import USER_ROLE

User = get_user_model()


class UsernameField(serializers.Field):
    NOW_ALLOWED_USERNAMES = ['me']
    ERROR_REGEX_MESSAGE = ('username может состоять только из букв, '
                           'цифр и спецсимволов: @.+-_')

    def to_representation(self, value):
        return value
    
    def to_internal_value(self, data):
        if data in self.NOW_ALLOWED_USERNAMES:
            raise serializers.ValidationError({
                'username': 'This field is required.'
            })
        if re.search(r'^[\w.@+-]+\Z', data) is None:
            raise serializers.ValidationError(self.ERROR_REGEX_MESSAGE)
        if User.objects.filter(username=data).exists():
            raise serializers.ValidationError({
                'username': 'This field is required.'
            })
        return data


class RegistrationSerializer(serializers.Serializer):
    """ Сериализация регистрации пользователя и создания нового. """
    username = UsernameField()
    email = serializers.EmailField()


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
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
