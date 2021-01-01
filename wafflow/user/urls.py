from django.urls import include, path
from rest_framework.routers import SimpleRouter
from user.views import UserViewSet, UserListViewSet

app_name = "user"

router = SimpleRouter()
router.register("users", UserListViewSet, basename="users")
router.register("user", UserViewSet, basename="user")  # user/

urlpatterns = [
    path("", include((router.urls))),
]
