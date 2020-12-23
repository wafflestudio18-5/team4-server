from rest_framework import serializers
from question.models import UserQuestion


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
        return UserQuestion.objects.filter(question=question, bookmark=True).count()
