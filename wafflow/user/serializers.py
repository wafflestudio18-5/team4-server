from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from user.models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(allow_blank=False)
    password = serializers.CharField(allow_blank=False, write_only=True)
    email = serializers.EmailField(allow_blank=False)
    last_login = serializers.DateTimeField(read_only=True)
    nickname = serializers.CharField(allow_blank=False, write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'email',
            'last_login',
            'nickname',
        )

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        nickname = data.get('nickname')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already exists")
        if UserProfile.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError("Nickname already exists")
        return data

    @transaction.atomic
    def create(self, validated_data):
        nickname = validated_data.pop('nickname')

        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)

        UserProfile.objects.create(user=user, nickname=nickname)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    email = serializers.EmailField(source='user.email')
    last_login = serializers.DateTimeField(read_only=True, source='user.last_login')
    nickname = serializers.CharField(allow_blank=False)
    picture = serializers.CharField(required=False)
    reputation = serializers.IntegerField(required=False)

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'username',
            'created_at',
            'updated_at',
            'email',
            'last_login',
            'nickname',
            'picture',
            'reputation',
        )