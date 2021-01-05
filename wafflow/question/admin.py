from django.contrib import admin

from .models import Question, UserQuestion, Tag, QuestionTag
from answer.models import Answer


class UserQuestionInline(admin.TabularInline):
    model = UserQuestion
    readonly_fields = ["rating", "user", "bookmark", "bookmark_at"]


class QuestionTagInline(admin.TabularInline):
    model = QuestionTag
    readonly_fields = ["tag"]


class AnswerTagInline(admin.TabularInline):
    model = Answer
    readonly_fields = ["content", "user", "is_accepted", "vote"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [(None, {"fields": ["user", "title", "content", "is_active"]})]
    readonly_fields = ["user", "title", "content"]
    inlines = [
        QuestionTagInline,
        UserQuestionInline,
        AnswerTagInline,
    ]
    list_display = (
        "title",
        "user",
        "view_count",
        "created_at",
        "updated_at",
        "vote",
        "has_accepted",
        "is_active",
    )
    list_filter = ["created_at", "has_accepted", "vote", "is_active"]
    search_fields = ["title", "content"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fieldsets = [("Tag name", {"fields": ["name"]})]
    readonly_fields = ["name"]
    list_display = ("name", "created_at")
    list_filter = ["created_at"]
    search_fields = ["name"]
