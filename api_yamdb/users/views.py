import email
from random import randint, random
from urllib import request

from api.paginators import StandardResultsSetPagination
from api.permissions import OnlyAdmin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import RECIPIENTS_EMAIL

from . import serializers
from .models import User


@api_view(['POST'])
def registration(request):
    serializer = serializers.RegistrationSerializer(data=request.data)
    userpostname = serializer.initial_data.get('username')
    userpostemail = serializer.initial_data.get('email')
    if User.objects.filter(email=userpostemail).exists():
        message = ('Эта почта уже зарегистрирована')
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=userpostname).exists():
        message = ('Этот никнейм уже занят!')
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(
        username=userpostname, email=userpostemail).exists():
        user = get_object_or_404(User, username=userpostname)
        data = user.confirmation_code
        send_mail(
            'Регистрация нового пользователя',
            'Это ваш token для получения JWTТокена:' f'{data}',
            RECIPIENTS_EMAIL,
            [user.email],
        )
        message = (
            f'Письмо с кодом подтверждения'
            f'повторно направлено вам на почту!'
        )
        return Response(message, status=status.HTTP_200_OK)
    if serializer.is_valid():
        User.objects.create_user(
            username=userpostname, email=userpostemail, confirmation_code=randint(100000, 1000000))
        user = get_object_or_404(User, username=userpostname)
        data = user.confirmation_code
        send_mail(
            'Регистрация нового пользователя',
            'Это ваш token для получения JWTТокена:' f'{data}',
            RECIPIENTS_EMAIL,
            [userpostemail],
        )
        message = (
            f'Письмо с кодом подтверждения'
            f'повторно направлено вам на почту!'
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JWTView(APIView):

    def post(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        if not username or not confirmation_code:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        usercheck = get_object_or_404(User, username=username)
        if confirmation_code == usercheck.confirmation_code:
            token = RefreshToken.for_user(usercheck)
            return Response({
                'token': str(token.access_token)}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (OnlyAdmin,)
    lookup_field = 'username'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username',)
    pagination_class = StandardResultsSetPagination

    @action(
        methods=('get', 'patch'),
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,),
        serializer_class=serializers.UserSerializer
    )
    def user_info(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
