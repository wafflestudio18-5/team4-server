from django.urls import path
from rate.views import RateViewSet

app_name = 'rate'

urlpatterns = [
    path("rate/question/<int:pk>/", RateViewSet.rate_question),
    path("rate/answer/<int:pk>/", RateViewSet.rate_answer),
    path("rate/comment/<int:pk>/", RateViewSet.rate_comment),
]
