from django.urls import include, path
from rest_framework.routers import SimpleRouter

from comment.views import CommentViewSet, CommentAnswerViewSet, CommentQuestionViewSet


app_name = "comment"

router = SimpleRouter()
comment_question_detail = CommentQuestionViewSet.as_view(
    {"get": "retrieve", "post": "make"}
)
comment_answer_detail = CommentAnswerViewSet.as_view(
    {"get": "retrieve", "post": "make"}
)

router.register("comment", CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
    path("comment/question/<int:pk>/", comment_question_detail),
    path("comment/answer/<int:pk>/", comment_answer_detail),
]
