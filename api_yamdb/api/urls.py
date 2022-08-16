from django.urls import path, include
from rest_framework import routers

from . import views

router_v1 = routers.SimpleRouter()
router_v1.register(
    r'titles/',
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
    path(r'v1/', include(router_v1.urls))
]
