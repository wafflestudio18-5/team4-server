from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("answer.urls")),
    path("api/", include("question.urls")),
    path("api/", include("comment.urls")),
    path("api/", include("user.urls")),
    path("api/", include("bookmark.urls")),
    path("api/", include("rate.urls")),
    path("api/", include("tag.urls")),
] + static(settings.MEDIA_LOCATION, document_root=settings.MEDIA_ROOT)
