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

from reviews.models import (Review, Title, Genre, Category, User,
                            START_RANGE_CONFIRMATION_CODE,
                            END_RANGE_CONFIRMATION_CODE,
                            NOT_PIN_CONFIRMATION_CODE)

from . import paginators, permissions, serializers
from .filters import TitleFilter


def set_confirmation_code(user):
    user.confirmation_code = str(randint(START_RANGE_CONFIRMATION_CODE,
                                         END_RANGE_CONFIRMATION_CODE))
    user.save()


class BaseGenreCategoryViewSet(mixins.ListModelMixin,
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


class CategoryViewSet(BaseGenreCategoryViewSet):
    """Endpoint модели Category."""
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class GenreViewSet(BaseGenreCategoryViewSet):
    """Endpoint модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Endpoint модели Title."""
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (permissions.OnlyAdminOrRead,)
    pagination_class = paginators.StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    ordering_fields = ('-rating', 'category', 'name', 'year')

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
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        try:
            user, _ = User.objects.get_or_create(
                username=username,
                email=email
            )
        except IntegrityError:
            return Response('username or email already exists.',
                            status=status.HTTP_400_BAD_REQUEST)
        set_confirmation_code(user)
        send_mail(
            'Регистрация пользователя',
            f'Это ваш confirmation_code: {user.confirmation_code}',
            settings.RECIPIENTS_EMAIL,
            [email],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class JWTView(APIView):

    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        confirmation_code = serializer.data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if (user.confirmation_code != confirmation_code
                or user.confirmation_code == NOT_PIN_CONFIRMATION_CODE):
            user.confirmation_code = NOT_PIN_CONFIRMATION_CODE
            user.save()
            return Response(status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken.for_user(user)
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
        permission_classes=(IsAuthenticated,)
    )
    def user_info(self, request):
        user = request.user
        if request.method == 'GET':
            return Response(
                self.get_serializer(user).data,
                status=status.HTTP_200_OK
            )
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)
