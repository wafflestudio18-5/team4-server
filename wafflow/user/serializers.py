from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from user.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=False, write_only=True)
    email = serializers.EmailField(required=True)
    last_login = serializers.DateTimeField(read_only=True)
    nickname = serializers.CharField(required=False, allow_blank=True, write_only=True)
    picture = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "email",
            "last_login",
            "nickname",
            "picture",
        )

    def validate_password(self, value):
        return make_password(value)

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.get("email")
        username = validated_data.get("username")
        password = validated_data.get("password")
        nickname = validated_data.pop("nickname")
        picture = validated_data.pop("picture", None)

        if not password or password == "":
            raise serializers.ValidationError("Password required!")
        if not nickname or nickname == "":
            raise serializers.ValidationError("Nickname required!")
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already exists")
        if UserProfile.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError("Nickname already exists")

        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)
        user.is_active = True
        user.save()

        UserProfile.objects.create(user=user, nickname=nickname, picture=picture)
        return user

    @transaction.atomic
    def update(self, user, validated_data):
        password = validated_data.get("password")
        user.set_password(password)
        user.save()

        userprofile = user.profile
        nickname = validated_data.pop("nickname", None)
        picture = validated_data.pop("picture", None)
        if nickname and nickname != "":
            userprofile.nickname = nickname
        if picture and picture != "":
            userprofile.picture = picture
        userprofile.save()

        return super(UserSerializer, self).update(user, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True, source="user.username")
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    email = serializers.EmailField(read_only=True, source="user.email")
    last_login = serializers.DateTimeField(read_only=True, source="user.last_login")
    nickname = serializers.CharField()
    picture = serializers.CharField()
    reputation = serializers.IntegerField()

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "username",
            "created_at",
            "updated_at",
            "email",
            "last_login",
            "nickname",
            "picture",
            "reputation",
        )


class AuthorSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    reputation = serializers.IntegerField(source="profile.reputation")

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "reputation",
        )
