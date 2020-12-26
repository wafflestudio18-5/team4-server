from django.urls import include, path
from rest_framework.routers import SimpleRouter
from bookmark.views import BookmarkQuestionViewSet, BookmarkUserViewSet

app_name = "bookmark"

router = SimpleRouter()

router.register("bookmark/user", BookmarkUserViewSet, basename="bookmark_user")

bookmark_question_detail = BookmarkQuestionViewSet.as_view(
    {"post": "make", "delete": "destroy"}
)

urlpatterns = [
    path("", include(router.urls)),
    path("bookmark/question/<int:pk>/", bookmark_question_detail),
]
