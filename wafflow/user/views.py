from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from user.serializers import UserSerializer, UserProfileSerializer, AuthorSerializer

from user.models import UserProfile
from question.models import UserQuestion, Question
from answer.models import UserAnswer, Answer


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        if self.action in ("create", "login", "retrieve"):
            return (AllowAny(),)
        return self.permission_classes

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return UserSerializer
        return UserProfileSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        login(request, user)

        data = UserProfileSerializer(user.profile).data
        data["token"] = user.auth_token.key
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["PUT"])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user and user.is_active == True:
            login(request, user)

            data = self.get_serializer(user.profile).data
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
            if not request.user.is_authenticated:
                return Response(
                    {"message": "Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED
                )
            user = request.user
            data = self.get_serializer(user.profile).data
            data["answer_count"] = Answer.objects.filter(
                user=user, is_active=True
            ).count()
            data["bookmark_count"] = user.user_questions.filter(
                bookmark=True, question__is_active=True
            ).count()
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

        serializer = self.get_serializer(user, data=data)
        serializer.is_valid()
        serializer.save()

        data = UserProfileSerializer(user.profile).data
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
            user.save()
            logout(request)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
