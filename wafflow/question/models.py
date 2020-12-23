from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    user = models.ForeignKey(User, related_name="questions", on_delete=models.CASCADE);
    view_count = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=5000)
    is_active = models.BooleanField(default=True)
    has_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vote = models.IntegerField(default=0)


class UserQuestion(models.Model):
    INCREMENT = 1
    DECREMENT = -1
    NONE = 0

    RATING_DEGREE = (
        (INCREMENT, INCREMENT),
        (NONE, NONE),
        (DECREMENT, DECREMENT),
    )

    rating = models.IntegerField(choices=RATING_DEGREE)
    bookmark = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name="user_questions", on_delete=models.CASCADE);
    question = models.ForeignKey(Question, related_name="user_questions", on_delete=models.CASCADE);


class Tag(models.Model):
    name = models.CharField(max_length=20)


class QuestionTag(models.Model):
    question = models.ForeignKey(Question, related_name="question_tags", on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, related_name="question_tags", on_delete=models.CASCADE)
