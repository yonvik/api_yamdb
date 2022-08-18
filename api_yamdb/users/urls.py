from django.urls import path

from .views import RegistrationAPIView, JWTView

app_name = 'users'

urlpatterns = [
    path('auth/signup/', RegistrationAPIView.as_view()),
    path('auth/token/', JWTView.as_view())
]
