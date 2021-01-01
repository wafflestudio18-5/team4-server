from django.urls import include, path
from rest_framework.routers import SimpleRouter
from tag.views import TagViewSet, TagListViewSet

app_name = "tag"

router = SimpleRouter()

router.register("tag/user", TagViewSet, basename="tag")
router.register("tags", TagListViewSet, basename="tag_list")

urlpatterns = [
    path("", include(router.urls)),
]
