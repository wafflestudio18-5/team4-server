from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from user.models import UserProfile
from answer.models import Answer
from question.models import Question, UserQuestion
from rest_framework.validators import UniqueValidator
from user.constants import *


class UserSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(write_only=True)
    picture = serializers.CharField(required=False, allow_blank=True, write_only=True)
    title = serializers.CharField(allow_blank=True, write_only=True, required=False)
    intro = serializers.CharField(allow_blank=True, write_only=True, required=False)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        allow_blank=False,
    )

    pop_list = [
        "nickname",
        "picture",
        "title",
        "intro",
    ]

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
            "title",
            "intro",
        )

    def validate_username(self, value):
        if self.instance is not None:
            raise serializers.ValidationError("changing username is not allowed")
        if len(value) > MAX_LENGTH:
            raise serializers.ValidationError("username is too long")
        return value

    def validate_email(self, value):
        if self.instance is not None:
            raise serializers.ValidationError("changing email is not allowed")
        return value

    def validate_password(self, value):
        return make_password(value)

    @transaction.atomic
    def create(self, validated_data):
        data = validated_data.copy()
        for pop in self.pop_list:
            validated_data.pop(pop, None)

        user = super(UserSerializer, self).create(validated_data)

        data["user_id"] = user.id
        Token.objects.create(user=user)

        user_profile_serializer = UserProfileProduceSerializer(data=data)
        user_profile_serializer.is_valid(raise_exception=True)
        user_profile_serializer.save()
        return user

    @transaction.atomic
    def update(self, user, validated_data):
        data = validated_data.copy()
        pop_list = self.pop_list.copy() + ["username", "email"]

        for pop in pop_list:
            validated_data.pop(pop, None)

        user_profile = user.profile
        user_profile_serializer = UserProfileProduceSerializer(
            user_profile, data=data, partial=True
        )
        user_profile_serializer.is_valid(raise_exception=True)
        user_profile_serializer.save()

        return super(UserSerializer, self).update(user, validated_data)


class UserProfileProduceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ("nickname", "picture", "title", "intro", "user_id", "github_id")

    def validate_github_id(self, value):
        if self.instance:
            raise serializers.ValidationError("github_id is not allowed to edit")
        if value is not None and UserProfile.objects.filter(github_id=value).exists():
            raise serializers.ValidationError(
                "user_profile with this github user is already exist"
            )
        return value

    def validate_user_id(self, value):
        if self.instance:
            raise serializers.ValidationError("user_id is not allowed to edit")
        if not User.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("active user is not exist")
        return value

    def create(self, validated_data):
        user_id = int(validated_data.pop("user_id"))
        user = User.objects.get(id=user_id)
        validated_data["user"] = user
        return super(UserProfileProduceSerializer, self).create(validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True, source="user.username")
    email = serializers.EmailField(read_only=True, source="user.email")
    last_login = serializers.DateTimeField(read_only=True, source="user.last_login")
    answer_count = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()

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
            "answer_count",
            "bookmark_count",
            "question_count",
            "title",
            "intro",
        )

    def get_answer_count(self, user_profile):
        return Answer.objects.filter(user=user_profile.user, is_active=True).count()

    def get_question_count(self, user_profile):
        return Question.objects.filter(user=user_profile.user, is_active=True).count()

    def get_bookmark_count(self, user_profile):
        return UserQuestion.objects.filter(
            user=user_profile.user, bookmark=True, question__is_active=True
        ).count()


class AuthorSerializer(serializers.ModelSerializer):
    picture = serializers.CharField(source="profile.picture")
    reputation = serializers.IntegerField(source="profile.reputation")
    nickname = serializers.CharField(source="profile.nickname")

    class Meta:
        model = User
        fields = (
            "id",
            "nickname",
            "picture",
            "reputation",
        )
