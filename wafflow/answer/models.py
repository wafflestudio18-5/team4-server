from django.db import models
from django.contrib.auth.models import User
from question.models import Question


class Answer(models.Model):
    content = models.CharField(max_length=5000)
    is_active = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="answers", on_delete=models.CASCADE)


class UserAnswer(models.Model):
    INCREMENT = 1
    DECREMENT = -1
    NONE = 0

    RATING_DEGREE = (
        (INCREMENT, INCREMENT),
        (NONE, NONE),
        (DECREMENT, DECREMENT),
    )

    rating = models.IntegerField(choices=RATING_DEGREE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name="user_answers", on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, related_name="user_answers", on_delete=models.CASCADE)
