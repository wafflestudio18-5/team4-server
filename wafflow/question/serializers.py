from rest_framework import serializers

from user.models import User, UserProfile
from question.models import Question, UserQuestion, Tag, QuestionTag


class QuestionSerializer(serializers.ModelSerializer):
    # user = serializers.SerializerMethodField()
    # question = serializers.SerializerMethodField()
    # bookmarked = serializers.BooleanField(source='bookmark')
    # author = serializers.CharField(source='user')
    # tags = serializers.CharField(source='tag')

    class Meta:
        model = Question
        fields = (
            'id',
            'title',
            'content',
            'vote',
            'view_count',
            'has_accepted',
            # 'bookmarked',
            'created_at',
            'updated_at',
            # 'author',
            # 'tags',
        )

        # def get_author(self, question):
        #     author_questions = question.user_questions.all().selected_related('author')
        #     return AuthorOfQuestionSerializer(author_questions).data

        # def get_tags(self, question):
        #     return TagSerializer(question.question_tags, many=True).data


class AuthorOfQuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    reputation = serializers.IntegerField(source='user.profile.reputation')

    class Meta:
        model = UserQuestion
        fields = (
            'id',
            'username',
            'reputation',
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
        )

