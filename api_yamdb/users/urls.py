from django.urls import path

from .views import LoginAPIView, RegistrationAPIView, MyTokenObtainPairView

app_name = 'users'

urlpatterns = [
    path('auth/signup/', RegistrationAPIView.as_view()),
    path('auth/token/', MyTokenObtainPairView.as_view())
]