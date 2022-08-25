from django.urls import path, include
from rest_framework import routers

from . import views

router_v1 = routers.SimpleRouter()
router_v1.register('users', views.UserViewSet, basename='users')
router_v1.register(
    r'titles',
    views.TitleViewSet,
    basename='titles'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet,
    basename='comments'
)
router_v1.register(
    r'categories',
    views.CategoryViewSet,
    basename='categories')
router_v1.register(
    r'genres',
    views.GenreViewSet,
    basename='genres')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', views.RegistrationAPIView.as_view()),
    path('v1/auth/token/', views.JWTView.as_view())
]
