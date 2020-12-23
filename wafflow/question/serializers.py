from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers

from question.models import Question, Tag, UserQuestion


class SimpleQuestionSerializer(serializers.ModelSerializer):
    view_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Question
        fields = (
            'id',
            'view_count',
            'title',
            'vote',
            'has_accepted',
            'created_at',
            'updated_at',
        )


class QuestionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    bookmarked = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta(SimpleQuestionSerializer.Meta):
        fields = SimpleQuestionSerializer.Meta.fields + (
            'author',
            'bookmarked',
            'comment_count',
            'content',
            'rating',
            'tags',
        )

    def get_author(self, question):
        user = question.user
        return {
            "id": user.id,
            "username": user.username,
            # "reputation": user.profile.reputation,
        }

    def get_bookmarked(self, question):
        user = self.context['request'].user
        if isinstance(user, AnonymousUser):
            return False
        try:
            user_question = question.user_questions.get(user=user)
        except UserQuestion.DoesNotExist:
            return False
        return user_question.bookmark

    def get_comment_count(self, question):
        return question.comments.filter(is_active=True).count()

    def get_rating(self, question):
        user = self.context['request'].user
        if isinstance(user, AnonymousUser):
            return 0
        try:
            user_question = question.user_questions.get(user=user)
        except UserQuestion.DoesNotExist:
            return 0
        return user_question.rating

    def get_tags(self, question):
        return QuestionTagSerializer(question.question_tags, many=True).data


class QuestionProduceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ('title', 'content',)

    def create(self, validated_data):
        user = self.context['request'].user
        return Question.objects.create(**validated_data, user=user)


class QuestionEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("title", "content",)


class QuestionTagSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ('id', 'name',)

    def get_id(self, question_tags):
        return question_tags.tag_id

    def get_name(self, question_tags):
        return Tag.objects.get(id=question_tags.tag_id).name
