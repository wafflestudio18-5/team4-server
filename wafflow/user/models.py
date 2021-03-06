from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    nickname = models.CharField(max_length=16, unique=True)
    intro = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=50, blank=True)
    view_count = models.IntegerField(default=0)
    reputation = models.IntegerField(default=0)
    picture = models.ImageField(upload_to="profile_image", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    github_id = models.IntegerField(null=True)
