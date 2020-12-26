from rest_framework import serializers
from answer.models import Answer, UserAnswer
from django.contrib.auth.models import AnonymousUser

from user.serializers import AuthorSerializer
from question.models import Question


class SimpleAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ("id", "created_at", "updated_at", "vote", "is_accepted")


class AnswerSummarySerializer(SimpleAnswerSerializer):
    title = serializers.CharField(source="question.title", read_only=True)

    class Meta(SimpleAnswerSerializer.Meta):
        fields = SimpleAnswerSerializer.Meta.fields + ("title",)


class AnswerInfoSerializer(SimpleAnswerSerializer):
    rating = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta(SimpleAnswerSerializer.Meta):
        fields = SimpleAnswerSerializer.Meta.fields + (
            "content",
            "comment_count",
            "rating",
            "author",
        )

    def get_rating(self, answer):
        user = self.context["request"].user
        if isinstance(user, AnonymousUser):
            return 0
        try:
            user_answer = answer.user_answers.get(user=user)
        except UserAnswer.DoesNotExist:
            return 0
        return user_answer.rating

    def get_author(self, answer):
        user = answer.user

        return AuthorSerializer(user).data

    def get_comment_count(self, answer):
        return answer.comments.filter(is_active=True).count()


class AnswerProduceSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Answer
        fields = ("content", "question_id")

    def create(self, validated_data):
        user = self.context["request"].user
        question = Question.objects.get(pk=validated_data.pop("question_id"))
        return Answer.objects.create(**validated_data, user=user, question=question)


class AnswerEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ("content",)


class AnswerAcceptionSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source="question.id", read_only=True)
    has_accepted = serializers.BooleanField(
        source="question.has_accepted", read_only=True
    )
    answer_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = Answer
        fields = (
            "question_id",
            "has_accepted",
            "answer_id",
            "is_accepted",
        )
