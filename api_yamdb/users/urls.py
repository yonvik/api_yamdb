from django.urls import path

from .views import LoginAPIView, RegistrationAPIView, PatchProfileDataAPIView

app_name = 'users'

urlpatterns = [
    path('auth/signup/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
]