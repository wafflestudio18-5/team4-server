from django.contrib import admin

from .models import Comment, UserComment


class UserCommentInline(admin.TabularInline):
    model = UserComment
    readonly_fields = ["rating", "user"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {"fields": ["user", "type", "question", "answer", "content", "is_active"]},
        )
    ]
    readonly_fields = ["user", "type", "question", "answer", "content"]
    inlines = [
        UserCommentInline,
    ]
    list_display = (
        "type",
        "user",
        "created_at",
        "updated_at",
        "vote",
        "is_active",
    )
    list_filter = ["created_at", "updated_at", "vote", "type"]
    search_fields = ["content"]
