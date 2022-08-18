from django.urls import path, include

from .views import RegistrationAPIView, JWTView, UserMeApiView

from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter() 
router.register(r'users', UserViewSet, basename='users')
router.register(r'users/(?P<username>[\w.@+-]+)/', UserViewSet)
router.register(r'users/me/', UserMeApiView, basename='users/me')

app_name = 'users'

urlpatterns = [
    path('auth/signup/', RegistrationAPIView.as_view()),
    path('auth/token/', JWTView.as_view()),
    path('', include(router.urls))

]
