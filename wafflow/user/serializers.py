from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from user.models import UserProfile
from answer.models import Answer
from question.models import Question, UserQuestion


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    last_login = serializers.DateTimeField(read_only=True)
    nickname = serializers.CharField(allow_blank=True, write_only=True)
    picture = serializers.CharField(required=False, allow_blank=True, write_only=True)
    title = serializers.CharField(allow_blank=True, write_only=True, required=False)
    intro = serializers.CharField(allow_blank=True, write_only=True, required=False)

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

    def validate_password(self, value):
        return make_password(value)

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.get("email")
        username = validated_data.get("username")
        password = validated_data.get("password")
        nickname = validated_data.pop("nickname")
        picture = validated_data.pop("picture", "")
        title = validated_data.pop("title", None)
        intro = validated_data.pop("intro", None)

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already exists")
        if UserProfile.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError("Nickname already exists")

        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)

        UserProfile.objects.create(user=user, nickname=nickname, picture=picture)
        return user

    @transaction.atomic
    def update(self, user, validated_data):
        user_profile = user.profile
        nickname = validated_data.pop("nickname", None)
        picture = validated_data.pop("picture", None)
        title = validated_data.pop("title", None)
        intro = validated_data.pop("intro", None)
        if nickname and nickname != "":
            user_profile.nickname = nickname
        if picture and picture != "":
            user_profile.picture = picture
        if title is not None:
            user_profile.title = title
        if intro is not None:
            user_profile.intro = intro
        user_profile.save()

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
