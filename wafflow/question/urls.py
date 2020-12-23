from django.urls import include, path
from rest_framework.routers import SimpleRouter
from question.views import QuestionViewSet

app_name = 'question'

router = SimpleRouter()
router.register('question', QuestionViewSet, basename='question')  # /api/v1/question/

urlpatterns = [
    path('', include((router.urls))),
]

#/question/search/keywords/?keywords={}&filter_by={}&sorted_by={}&page={}