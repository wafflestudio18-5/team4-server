from django.urls import include, path
from rest_framework.routers import SimpleRouter
from answer.views import AnswerUserViewSet, AnswerQuestionViewSet, AnswerViewSet

app_name = "answer"

router = SimpleRouter()
answer_question_detail = AnswerQuestionViewSet.as_view(
    {"get": "retrieve", "post": "make"}
)

router.register("answer", AnswerViewSet, basename="answer")
router.register("answer/user", AnswerUserViewSet, basename="answer_user")


urlpatterns = [
    path("", include(router.urls)),
    path("answer/question/<int:pk>/", answer_question_detail),
]
