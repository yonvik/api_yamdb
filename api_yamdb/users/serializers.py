from rest_framework import serializers, status
from django.contrib.auth import get_user_model

from . import exceptions

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """ Сериализация регистрации пользователя и создания нового. """
    # Клиентская сторона не должна иметь возможность отправлять токен вместе с
    # запросом на регистрацию. Сделаем его доступным только на чтение.
    NOT_ALLOWED_USERNAMES = ['me']

    class Meta:
        model = User
        # Перечислить все поля, которые могут быть включены в запрос
        # или ответ, включая поля, явно указанные выше.
        fields = [
            'email',
            'username',
            'role',
            'bio',
            'first_name',
            'last_name'
        ]

    def create(self, validated_data):
        # Использовать метод create_user, который мы
        # написали ранее, для создания нового пользователя.
        return User.objects.create_user(**validated_data)

    def validate_username(self, value):
        if value in self.NOT_ALLOWED_USERNAMES:
            raise serializers.ValidationError(
                'Поле username не может содержать значение: ', value
            )
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    token = serializers.CharField(max_length=255, read_only=True)
    confirmation_code = serializers.CharField(max_length=256, required=True)

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise exceptions.CustomValidation(
                'user does not exist',
                status_code=status.HTTP_404_NOT_FOUND
            )
        return value

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        user = User.objects.get(username=username)
        if user.secret_key == confirmation_code:
            data.update({'token': user.token})
            return data
        raise serializers.ValidationError(
            'not valid confirmation_code: ', confirmation_code)


class UserInfoSerializer(RegistrationSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'bio', 'role'
        )
