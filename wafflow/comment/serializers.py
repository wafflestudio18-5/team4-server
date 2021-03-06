from rest_framework import serializers
from django.contrib.auth.models import AnonymousUser

from answer.models import Answer
from comment.models import Comment, UserComment
from question.models import Question
from user.serializers import AuthorSerializer


class SimpleCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "created_at",
            "updated_at",
            "content",
            "vote",
        )


class CommentSerializer(SimpleCommentSerializer):
    author = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta(SimpleCommentSerializer.Meta):
        fields = SimpleCommentSerializer.Meta.fields + (
            "author",
            "rating",
        )

    def get_author(self, comment):
        user = comment.user
        return AuthorSerializer(user).data

    def get_rating(self, comment):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if isinstance(user, AnonymousUser):
            return 0
        try:
            user_comment = comment.user_comments.get(user=user)
        except UserComment.DoesNotExist:
            return 0
        return user_comment.rating


class CommentsSerializer(CommentSerializer):
    comments = serializers.SerializerMethodField()

    class Meta(CommentSerializer.Meta):
        model = Question
        fields = ("comments",)

    def get_comments(self, comments):
        return CommentSerializer(comments, many=True).data


class CommentEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content",)


class CommentAnswerProduceSerializer(serializers.ModelSerializer):
    answer_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Comment
        fields = (
            "content",
            "answer_id",
        )

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        answer = Answer.objects.get(pk=validated_data.pop("answer_id"))
        return Comment.objects.create(
            **validated_data, user=user, answer=answer, type=Comment.ANSWER
        )


class CommentQuestionProduceSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Comment
        fields = (
            "content",
            "question_id",
        )

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        question = Question.objects.get(pk=validated_data.pop("question_id"))
        return Comment.objects.create(
            **validated_data, user=user, question=question, type=Comment.QUESTION
        )
