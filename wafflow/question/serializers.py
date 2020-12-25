from rest_framework import serializers

from question.models import Question, Tag, UserQuestion
from question.constants import CONTENT_FOR_TAG_SEARCH


class SimpleQuestionSerializer(serializers.ModelSerializer):
    view_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "view_count",
            "title",
            "vote",
            "has_accepted",
            "created_at",
            "updated_at",
        )


class QuestionUserSerializer(SimpleQuestionSerializer):
    answer_count = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()

    class Meta(SimpleQuestionSerializer.Meta):
        fields = SimpleQuestionSerializer.Meta.fields + (
            "answer_count",
            "bookmark_count",
        )

    def get_answer_count(self, question):
        return question.answers.filter(is_active=True).count()

    def get_bookmark_count(self, question):
        return question.user_questions.filter(bookmark=True).count()


class QuestionSerializer(QuestionUserSerializer):
    author = serializers.SerializerMethodField()
    bookmarked = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta(QuestionUserSerializer.Meta):
        fields = QuestionUserSerializer.Meta.fields + (
            "author",
            "bookmarked",
            "comment_count",
            "rating",
            "tags",
        )

    def get_author(self, question):
        user = question.user
        return {
            "id": user.id,
            "username": user.username,
            "reputation": user.profile.reputation,
        }

    def get_bookmarked(self, question):
        user = self.context["request"].user
        try:
            user_question = question.user_questions.get(user=user)
        except UserQuestion.DoesNotExist:
            return False
        return user_question.bookmark

    def get_comment_count(self, question):
        return question.comments.filter(is_active=True).count()

    def get_rating(self, question):
        user = self.context["request"].user
        try:
            user_question = question.user_questions.get(user=user)
        except UserQuestion.DoesNotExist:
            return 0
        return user_question.rating

    def get_tags(self, question):
        return QuestionTagSerializer(question.question_tags, many=True).data


class QuestionInfoSerializer(QuestionSerializer):
    content = serializers.CharField(source="question.content")

    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ("content",)


class QuestionTagSearchSerializer(QuestionSerializer):
    content = serializers.SerializerMethodField()

    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ("content",)

    def get_content(self, question):
        return question.content[0:CONTENT_FOR_TAG_SEARCH]


class QuestionProduceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            "title",
            "content",
        )

    def create(self, validated_data):
        user = self.context["request"].user
        return Question.objects.create(**validated_data, user=user)


class QuestionEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            "title",
            "content",
        )


class QuestionTagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="question_tag.tag.id", read_only=True)
    name = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
        )

    def get_name(self, question_tag):
        return Tag.objects.get(id=question_tag.tag.id).name
