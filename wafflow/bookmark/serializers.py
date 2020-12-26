from rest_framework import serializers
from question.models import UserQuestion
from question.serializers import SimpleQuestionUserSerializer, QuestionTagSerializer
from user.serializers import AuthorSerializer


class SimpleBookmarkSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    question_id = serializers.IntegerField(source="question.id", read_only=True)
    bookmark_count = serializers.SerializerMethodField()
    bookmarked = serializers.BooleanField(source="bookmark", read_only=True)

    class Meta:
        model = UserQuestion
        fields = ("user_id", "question_id", "bookmark_count", "bookmarked")

    def get_bookmark_count(self, user_question):
        question = user_question.question
        return UserQuestion.objects.filter(
            question=question, bookmark=True, question__is_active=True
        ).count()


class BookmarkQuestionSerializer(SimpleQuestionUserSerializer):
    tags = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta(SimpleQuestionUserSerializer.Meta):
        fields = SimpleQuestionUserSerializer.Meta.fields + ("tags", "author")

    def get_tags(self, question):
        return QuestionTagSerializer(question.question_tags, many=True).data

    def get_author(self, question):
        return AuthorSerializer(question.user).data
