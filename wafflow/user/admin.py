from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import User, UserProfile
from question.models import UserQuestion
from answer.models import UserAnswer
from comment.models import UserComment


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    readonly_fields = [
        "view_count",
        "reputation",
        "nickname",
        "intro",
        "title",
        "picture",
        "github_id",
    ]


class UserQuestionInline(admin.TabularInline):
    model = UserQuestion
    readonly_fields = ["rating", "user", "bookmark", "bookmark_at", "question"]


class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    readonly_fields = ["rating", "user", "answer"]


class UserCommentInline(admin.TabularInline):
    model = UserComment
    readonly_fields = ["rating", "user", "comment"]


class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Personal info", {"fields": ("username", "email", "password")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    readonly_fields = [
        "username",
        "email",
        "password",
        "last_login",
        "date_joined",
        "is_staff",
        "is_superuser",
        "groups",
        "user_permissions",
    ]
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
    search_fields = ("username", "email", "profile__nickname")


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
