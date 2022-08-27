from random import randint

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from . import paginators
from . import permissions
from . import serializers
from .filters import TitleFilter
from reviews import models as review_models


class CustomViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    permission_classes = (permissions.OnlyAdminOrRead,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    pagination_class = paginators.StandardResultsSetPagination


class ReviewViewSet(viewsets.ModelViewSet):
    """Endpoint модели Review."""
    serializer_class = serializers.ReviewSerializer
    permission_classes = (
        permissions.OnlyContributionAdminModeratorOrRead,)
    pagination_class = paginators.StandardResultsSetPagination

    def get_title(self):
        return get_object_or_404(
            review_models.Title,
            pk=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        author = self.request.user
        title = self.get_title()
        serializer.save(author=author, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Endpoint модели Comment."""
    serializer_class = serializers.CommentSerializer
    permission_classes = (
        permissions.OnlyContributionAdminModeratorOrRead,)
    pagination_class = paginators.StandardResultsSetPagination

    def get_review(self):
        return get_object_or_404(review_models.Review,
                                 pk=self.kwargs['review_id'],
                                 title__pk=self.kwargs['title_id'])

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        author = self.request.user
        review = self.get_review()
        serializer.save(author=author, review=review)


class CategoryViewSet(CustomViewSet):
    """Endpoint модели Category."""
    queryset = review_models.Category.objects.all()
    serializer_class = serializers.CategorySerializer


class GenreViewSet(CustomViewSet):
    """Endpoint модели Genre."""
    queryset = review_models.Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Endpoint модели Title."""
    queryset = review_models.Title.objects.annotate(
        rating=Avg('reviews__score'))
    permission_classes = (permissions.OnlyAdminOrRead,)
    pagination_class = paginators.StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    ordering_fields = ('-rating',)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return serializers.TitleSerializer
        return serializers.TitleCreateSerializer


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        userpostname = serializer.initial_data.get('username')
        userpostemail = serializer.initial_data.get('email')
        if review_models.User.objects.filter(email=userpostemail).exists():
            message = ('Эта почта уже зарегистрирована')
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        if review_models.User.objects.filter(username=userpostname).exists():
            message = ('Этот никнейм уже занят!')
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        if review_models.User.objects.filter(
                username=userpostname, email=userpostemail).exists():
            user = get_object_or_404(review_models.User, username=userpostname)
            data = user.confirmation_code
            send_mail(
                'Регистрация нового пользователя',
                'Это ваш token для получения JWTТокена:' f'{data}',
                settings.RECIPIENTS_EMAIL,
                [user.email],
            )
            message = ('Письмо с кодом подтверждения\n'
                       'повторно направлено вам на почту!')
            return Response(message, status=status.HTTP_200_OK)
        if serializer.is_valid():
            user = review_models.User.objects.create_user(
                username=userpostname,
                email=userpostemail,
                confirmation_code=randint(100000, 1000000))
            user.role = request.data.get('role'),
            user.save()
            user = get_object_or_404(review_models.User, username=userpostname)
            data = user.confirmation_code
            send_mail(
                'Регистрация нового пользователя',
                'Это ваш token для получения JWTТокена:' f'{data}',
                settings.RECIPIENTS_EMAIL,
                [userpostemail],
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JWTView(APIView):
    serializer_class = serializers.LoginSerializer

    def get_serializer(self):
        return self.serializer_class(data=self.request.data)

    def post(self, request):
        serializer = self.get_serializer()
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        if not confirmation_code:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(review_models.User, username=username)
        if user.confirmation_code == confirmation_code:
            token = RefreshToken.for_user(user)
            return Response({'token': str(token.access_token)},
                            status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = review_models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.OnlyAdmin,)
    lookup_field = 'username'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username',)
    pagination_class = paginators.StandardResultsSetPagination

    @action(
        methods=('get', 'patch'),
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,),
        serializer_class=serializers.UserSerializer
    )
    def user_info(self, request):
        user = get_object_or_404(review_models.User, pk=request.user.id)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            if request.user.role == review_models.USER_ROLE:
                serializer.save(role=review_models.USER_ROLE)
            else:
                serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
