# views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from .models import CustomUser
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    GoogleAuthSerializer,
    UserSerializer
)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    serializer = GoogleAuthSerializer(data=request.data)
    if serializer.is_valid():
        try:
            idinfo = id_token.verify_oauth2_token(
                serializer.validated_data['id_token'],
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            email = idinfo['email']
            google_id = idinfo['sub']
            name = idinfo.get('name', '')
            picture = idinfo.get('picture', '')
            
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'google_id': google_id,
                    'profile_picture': picture,
                    'is_google_user': True,
                    'first_name': name.split(' ')[0] if name else '',
                    'last_name': ' '.join(name.split(' ')[1:]) if name else '',
                }
            )
            
            if not created and not user.is_google_user:
                user.google_id = google_id
                user.is_google_user = True
                user.profile_picture = picture
                user.save()
            
            tokens = get_tokens_for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'error': 'Invalid Google token'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)