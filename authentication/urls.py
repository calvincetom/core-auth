# urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('google-auth/', views.google_auth, name='google_auth'),
    path('profile/', views.user_profile, name='user_profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]