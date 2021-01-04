from django.contrib import admin

from .models import Answer, UserAnswer


class UserAnswerInline(admin.TabularInline):
    model = UserAnswer


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    fieldsets = [(None, {"fields": ["user", "question", "content", "is_active"]})]
    inlines = [
        UserAnswerInline,
    ]
    list_display = (
        "content",
        "user",
        "created_at",
        "updated_at",
        "vote",
        "is_accepted",
        "is_active",
    )
    list_filter = ["created_at", "is_accepted", "updated_at", "vote", "is_active"]
    search_fields = ["content", "question__title", "question__content"]
