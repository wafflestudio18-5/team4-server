from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from user.serializers import UserSerializer, UserProfileSerializer
from user.models import UserProfile


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated(), )

    def get_permissions(self):
        if self.action in ('create', 'login'):
            return (AllowAny(), )
        return self.permission_classes

    # POST /user
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save() 
        
        login(request, user)

        serializer = UserProfileSerializer(user.profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        data['token'] = user.auth_token.key
        return Response(data, status=status.HTTP_201_CREATED)

    # PUT /user/login
    @action(detail=False, methods=['PUT'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            data = UserProfileSerializer(user.profile).data
            token, created = Token.objects.get_or_create(user=user)
            data['token'] = token.key
            return Response(data)

        return Response({"message": "Authentication failed"}, status=status.HTTP_403_FORBIDDEN)

    # POST /user/logout
    @action(detail=False, methods=['POST'])
    def logout(self, request):
        logout(request)
        return Response()
        