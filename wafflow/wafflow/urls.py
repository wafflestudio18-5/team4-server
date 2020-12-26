from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("answer.urls")),
    path("", include("question.urls")),
    path("", include("comment.urls")),
    path("", include("user.urls")),
    path("", include("rate.urls")),
]
