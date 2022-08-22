import email
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters, status, viewsets
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

from . import serializers
from .models import User
from api.permissions import OnlyAdmin
from api.paginators import StandardResultsSetPagination
from django.core.mail import send_mail
from api_yamdb.settings import RECIPIENTS_EMAIL


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        userpostname = serializer.initial_data.get('username')
        userpostemail = serializer.initial_data.get('email')
        if User.objects.filter(username=userpostname, email=userpostemail).exists():
            user = get_object_or_404(User, username=userpostname)
            data = user.secret_key
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
                username=userpostname, email=userpostemail)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JWTView(APIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        serializer_class=serializers.UserInfoSerializer
    )
    def user_info(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
