from django.urls import include, path
from rest_framework.routers import SimpleRouter
from bookmark.views import BookmarkViewSet

app_name = "bookmark"

router = SimpleRouter()

bookmark_question_detail = BookmarkViewSet.as_view(
    {"post": "make", "delete": "destroy"}
)

urlpatterns = [
    path("", include(router.urls)),
    path("bookmark/question/<int:pk>/", bookmark_question_detail),
]
