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
from question.models import UserQuestion
from answer.models import UserAnswer


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        if self.action in ("create", "login"):
            return (AllowAny(),)
        return self.permission_classes

    def get_serializer_class(self):
        if self.action == ("create", "update"):
            return self.serializer_class
        return UserProfileSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        login(request, user)

        serializer = UserProfileSerializer(user.profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        data["token"] = user.auth_token.key
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["PUT"])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user and user.is_active == True:
            login(request, user)

            data = get_serializer(user.profile).data
            token, created = Token.objects.get_or_create(user=user)
            data["token"] = token.key
            return Response(data)

        return Response(
            {"message": "Authentication failed"}, status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=False, methods=["POST"])
    def logout(self, request):
        logout(request)
        return Response()

    def retrieve(self, request, pk=None):
        if pk == "me":
            user = request.user
            data = self.get_serializer(user.profile).data
            data["answer_count"] = user.user_answers.count()
            data["bookmark_count"] = user.user_questions.filter(bookmark=True).count()
            return Response(data)
        else:
            user = self.get_object()
            return Response(self.get_serializer(user.profile).data)

    def update(self, request, pk=None):
        if pk != "me":
            return Response(
                {"message": "Not allowed to edit user not me"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = request.user
        data = request.data

        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(user, serializer.validated_data)

        serializer = UserProfileSerializer(user.profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        if pk != "me":
            return Response(
                {"message": "Not allowed to edit user not me or this user"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = request.user
        if user.is_active == True:
            user.is_active = False
            logout(request)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
