from rest_framework import serializers
from answer.models import Answer, UserAnswer


class SimpleAnswerSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = (
            "id",
            "created_at",
            "updated_at",
            "rating",
            "is_accepted"
        )

    def get_rating(self,answer):



class AnswerSummarySerializer(SimpleAnswerSerializer):
    title = serializers.CharField(source="question.title", read_only=True)

    class Meta:
        fields = SimpleAnswerSerializer.Meta.fields + ("title",)


class AnswerInfoSerializer(SimpleAnswerSerializer):

    class Meta:
        fields = SimpleAnswerSerializer.Meta.fields + (
            "vote",
            "content",
            "comment_count"
        )
