from django.urls import path

from .views import LoginAPIView, RegistrationAPIView

app_name = 'users'

urlpatterns = [
    path('users/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
]