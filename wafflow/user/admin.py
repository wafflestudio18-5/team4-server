from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import User, UserProfile
from question.models import UserQuestion
from answer.models import UserAnswer
from comment.models import UserComment


class UserProfileInline(admin.TabularInline):
    model = UserProfile


class UserQuestionInline(admin.TabularInline):
    model = UserQuestion


class UserAnswerInline(admin.TabularInline):
    model = UserAnswer


class UserCommentInline(admin.TabularInline):
    model = UserComment


class UserProfileAdmin(UserAdmin):
    inlines = [
        UserProfileInline,
        UserQuestionInline,
        UserAnswerInline,
        UserCommentInline,
    ]

    list_display = (
        "username",
        "email",
        "is_staff",
        "profile",
        "is_active",
    )
    list_filter = ["is_staff", "is_active", "is_superuser"]
    search_fields = ("username",)


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
