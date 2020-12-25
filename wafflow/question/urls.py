from django.urls import include, path
from rest_framework.routers import SimpleRouter
from question.views import QuestionViewSet, QuestionUserViewSet, QuestionKeywordsViewSet

app_name = "question"

router = SimpleRouter()

router.register("question", QuestionViewSet, basename="question")
router.register("question/user", QuestionUserViewSet, basename="question_user")
router.register(
    "question/search/keywords", QuestionKeywordsViewSet, basename="question_keywords"
)

urlpatterns = [
    path("", include((router.urls))),
]
