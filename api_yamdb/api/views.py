from random import randint

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import (Review, Title, Genre, Category, User, USER_ROLE,
                            START_RANGE_CONFIRMATION_CODE,
                            END_RANGE_CONFIRMATION_CODE)

from . import paginators, permissions, serializers
from .filters import TitleFilter


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
            Title,
            pk=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Endpoint модели Comment."""
    serializer_class = serializers.CommentSerializer
    permission_classes = (
        permissions.OnlyContributionAdminModeratorOrRead,)
    pagination_class = paginators.StandardResultsSetPagination

    def get_review(self):
        return get_object_or_404(Review,
                                 pk=self.kwargs['review_id'],
                                 title__pk=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class CategoryViewSet(CustomViewSet):
    """Endpoint модели Category."""
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class GenreViewSet(CustomViewSet):
    """Endpoint модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Endpoint модели Title."""
    queryset = Title.objects.annotate(
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
        serializer.is_valid(raise_exception=True)
        userpostname = serializer.validated_data.get('username')
        userpostemail = serializer.validated_data.get('email')
        if (User.objects.filter(
                username=userpostname).exists()
                or User.objects.filter(
                    email=userpostemail).exists()):
            return Response(
                serializer.data, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(
                username=userpostname, email=userpostemail).exists():
            user = get_object_or_404(User, username=userpostname)
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
        user = User.objects.create_user(
            username=userpostname,
            email=userpostemail,
            confirmation_code=randint(START_RANGE_CONFIRMATION_CODE,
                                      END_RANGE_CONFIRMATION_CODE))
        user.save()
        user = get_object_or_404(User, username=userpostname)
        data = user.confirmation_code
        send_mail(
            'Регистрация нового пользователя',
            'Это ваш token для получения JWTТокена:' f'{data}',
            settings.RECIPIENTS_EMAIL,
            [userpostemail],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class JWTView(APIView):
    serializer_class = serializers.LoginSerializer

    def get_serializer(self):
        return self.serializer_class(data=self.request.data)

    def post(self, request):
        serializer = self.get_serializer()
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        confirmation_code = serializer.data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken.for_user(user)
        user.confirmation_code = None
        user.save()
        return Response({'token': str(token.access_token)},
                        status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
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
        user = self.request.user
        serializer = self.get_serializer(user)
        if self.request.method == 'PATCH':
            if user.role == USER_ROLE:
                return Response(serializer.data)
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)
