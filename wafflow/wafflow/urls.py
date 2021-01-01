from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("answer.urls")),
    path("", include("question.urls")),
    path("", include("comment.urls")),
    path("", include("user.urls")),
    path("", include("bookmark.urls")),
    path("", include("rate.urls")),
] + static(settings.MEDIA_LOCATION, document_root=settings.MEDIA_ROOT)
