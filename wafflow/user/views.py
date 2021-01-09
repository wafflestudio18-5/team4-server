from django.contrib.auth import authenticate, login, logout
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from django.db import transaction
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from user.serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserProfileProduceSerializer,
    AuthorSerializer,
)
from user.token import get_github_data
from user.models import UserProfile
from user.constants import *
from question.views import paginate_objects


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

    @transaction.atomic
    def create_github_user(self, request):
        github_data = get_github_data(request.data.get("github_token"))
        print(github_data)
        if github_data is None or github_data.get("id") is None:
            return Response(
                {"message": "Invalid github token"}, status=status.HTTP_400_BAD_REQUEST
            )
        github_id = int(github_data["id"])
        if UserProfile.objects.filter(github_id=github_id).exists():
            return Response(
                {"message": "User already signed up"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=f"{GITHUB}_{github_id}",
            password="github",
            email=github_data.get("email", ""),
        )
        request_data = request.data.copy()
        request_data["nickname"] = github_data["login"]
        request_data["github_id"] = github_id
        request_data["user_id"] = user.id
        Token.objects.create(user=user)
        serializer = UserProfileProduceSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = UserProfileSerializer(user.profile).data
        data["token"] = user.auth_token.key
        return Response(data, status=status.HTTP_201_CREATED)

    def create(self, request):
        request_data = request.data.copy()

        github_token = request_data.get("github_token")

        if github_token is not None:
            return self.create_github_user(request)

        request_data.pop("github_id", None)
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = UserProfileSerializer(user.profile).data
        data["token"] = user.auth_token.key
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["PUT"])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        github_token = request.data.get("github_token")

        if github_token is None or github_token == "":
            if username is None or len(username) > MAX_LENGTH:
                return Response(
                    {"message": "Authentication failed"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            user = authenticate(request, username=username, password=password)
        else:
            github_data = get_github_data(github_token)
            try:
                user = UserProfile.objects.get(github_id=github_data.get("id")).user
            except (UserProfile.DoesNotExist, AttributeError):
                return self.create_github_user(request)
        if user and user.is_active:
            data = self.get_serializer(user.profile).data
            token, created = Token.objects.get_or_create(user=user)
            data["token"] = token.key
            return Response(data)

        return Response(
            {"message": "Authentication failed"}, status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=False, methods=["POST"])
    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            return Response(
                {"message:token not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({})

    def retrieve(self, request, pk=None):
        if pk == "me":
            if not request.user.is_authenticated:
                return Response(
                    {"message": "Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED
                )
            user = request.user
        else:
            try:
                user = User.objects.get(pk=pk, is_active=True)
            except (User.DoesNotExist, ValueError):
                return Response(
                    {"message": "There is no user with that id"},
                    status=status.HTTP_404_NOT_FOUND,
                )

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
        if user.is_active:
            user.is_active = False
            user.save()
            logout(request)
            return Response({}, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_204_NO_CONTENT)


class UserListViewSet(viewsets.GenericViewSet):
    queryset = User.objects.filter(is_active=True)
    permission_classes = (AllowAny,)
    serializer_class = AuthorSerializer

    def list(self, request):
        search = request.query_params.get("search")
        if search is None or search == "":
            users = self.get_queryset()
        else:
            users = User.objects.filter(
                profile__nickname__icontains=search, is_active=True
            )

        users = sort_users(request, users)

        if users is None:
            return Response(
                {"message": "Invalid sorted_by"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        users = paginate_objects(request, users, USER_PER_PAGE)
        if users is None:
            return Response(
                {"message": "Invalid page"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "users": self.get_serializer(users, many=True).data,
                "user_count": User.objects.filter(is_active=True).count(),
            }
        )


def sort_users(request, users):
    sorted_by = request.query_params.get("sorted_by")
    if not (sorted_by in (REPUTATION, NEWEST)):
        return None
    if sorted_by == REPUTATION:
        users = users.order_by("-profile__reputation")
    elif sorted_by == NEWEST:
        users = users.order_by("-profile__created_at")
    return users
