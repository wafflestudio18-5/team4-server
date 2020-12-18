from django.db import models
from django.contrib.auth.models import User
from question.models import Question
from answer.models import Answer


class Comment(models.Model):
    QUESTION = "question"
    ANSWER = "answer"
    TYPE_CHOICES = (
        (QUESTION, QUESTION),
        (ANSWER, ANSWER)
    )

    content = models.CharField(max_length=500)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name="comments", on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, related_name="comments", on_delete=models.CASCADE)
    vote = models.IntegerField(default=0)


class UserComment(models.Model):
    INCREMENT = 1
    DECREMENT = -1
    NONE = 0

    RATING_DEGREE = (
        (INCREMENT, INCREMENT),
        (NONE, NONE),
        (DECREMENT, DECREMENT),
    )

    rating = models.IntegerField(choices=RATING_DEGREE)
    user = models.ForeignKey(User, related_name="user_comments", on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name="user_comments", on_delete=models.CASCADE);
