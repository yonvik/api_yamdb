from django.urls import include, path
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

signup_token_urlspatterns = [
    path('signup/', views.RegistrationAPIView.as_view(), name='send_code'),
    path('token/', views.JWTView.as_view(), name='get_token'),
]

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(signup_token_urlspatterns)),
]
