from django.db import models
from django.contrib.auth.models import User
from question.models import Tag


class UserTag(models.Model):
    user = models.ForeignKey(User, related_name="user_tags", on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, related_name="user_tags", on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
