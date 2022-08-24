from django.urls import path

from .views import JWTView, registration

app_name = 'users'

urlpatterns = [
    path('auth/signup/', registration),
    path('auth/token/', JWTView.as_view())
]