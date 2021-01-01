from rest_framework import serializers

from user.serializers import AuthorSerializer
from question.models import Tag
from tag.models import UserTag
from django.db.models import Q


class TagUserSerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()
    id = serializers.IntegerField(source="tag.id")
    name = serializers.CharField(source="tag.name")

    class Meta:
        model = UserTag
        fields = ("id", "name", "posts", "score")

    def get_posts(self, user_tag):
        user = user_tag.user

        return (
            user_tag.tag.question_tags.filter(
                question__is_active=True, tag=user_tag.tag
            )
            .filter(
                Q(question__user=user)
                | Q(question__answers__user=user, question__answers__is_active=True)
            )
            .distinct()
            .count()
        )


class TagListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ("id", "name", "created_at", "question_count")

    def get_question_count(self, tag):
        return tag.question_tags.filter(question__is_active=True).count()
