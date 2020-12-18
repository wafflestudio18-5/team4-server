from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    nickname = models.CharField(max_length=16)
    intro = models.CharField(max_length=200)
    view_count = models.IntegerField(default=0)
    reputation = models.IntegerField(default=0)