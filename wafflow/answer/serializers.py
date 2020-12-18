from rest_framework import serializers
from answer.models import Answer, UserAnswer


# from user.serializers import SimpleUserSerializer


class SimpleAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            "id",
            "created_at",
            "updated_at",
            "vote",
            "is_accepted"
        )


class AnswerSummarySerializer(SimpleAnswerSerializer):
    title = serializers.CharField(source="question.title", read_only=True)

    class Meta:
        fields = SimpleAnswerSerializer.Meta.fields + ("title",)


class AnswerInfoSerializer(SimpleAnswerSerializer):
    rating = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        fields = SimpleAnswerSerializer.Meta.fields + (
            "content",
            "comment_count",
            "rating"
        )

    def get_rating(self, answer):
        user = self.context['request'].user
        if user is None:
            return 0
        try:
            user_answer = answer.user_answers.objects.get(user=user)
        except UserAnswer.DoesNotExist:
            return 0
        return user_answer.rating

    def get_author(self, answer):
        user = answer.user
        return {
            "id": user.id,
            "username": user.username,
            "reputation": user.profile.reputation
        }
        # return SimpleUserSerializer(user).data

    def get_comment_count(self, answer):
        return answer.comments.filter(is_active=True).count()
