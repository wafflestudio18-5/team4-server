from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny

from django.db.models import Count, Q, Sum, When, Value, Case, F
from question.models import Tag
from question.views import paginate_objects
from tag.serializers import TagListSerializer, TagUserSerializer
from tag.constants import *
from tag.models import UserTag
from rest_framework.response import Response


class TagViewSet(viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagUserSerializer
    permission_classes = (AllowAny,)

    def retrieve(self, request, pk=None):
        if pk == "me":
            if not request.user.is_authenticated:
                return Response(
                    {"message": "Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED
                )
            user = request.user
        else:
            try:
                user = User.objects.get(pk=pk, is_active=True)
            except User.DoesNotExist:
                return Response(
                    {"message": "There is no user with that id"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        user_tags = UserTag.objects.filter(user=user)
        user_tags = sort_user_tag(request, user_tags)

        if user_tags is None:
            return Response(
                {"error": "Invalid sorted_by"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_tags = paginate_objects(request, user_tags, TAG_USER_PER_PAGE)
        if user_tags is None:
            return Response(
                {"error": "Invalid page"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"tags": self.get_serializer(user_tags, many=True).data})


class TagListViewSet(viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagListSerializer
    permission_classes = (AllowAny,)

    def list(self, request):
        tags = search_tag_list(request, self.get_queryset())
        tags = sort_tags_list(request, tags)
        if tags is None:
            return Response(
                {"error": "Invalid sorted_by"}, status=status.HTTP_400_BAD_REQUEST
            )

        tags = paginate_objects(request, tags, TAG_LIST_PER_PAGE)
        if tags is None:
            return Response(
                {"error": "Invalid page"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"tags": self.get_serializer(tags, many=True).data})


def search_tag_list(request, tags):
    search = request.query_params.get("search")
    if search is None or search == "":
        return tags
    return Tag.objects.filter(name__contains=search)


def sort_tags_list(request, tags):
    sorted_by = request.query_params.get("sorted_by")
    if not (sorted_by in (POPULAR, NAME, NEWEST)):
        return None
    if sorted_by == POPULAR:
        return tags.annotate(
            question_count=Count(
                "question_tags", filter=Q(question_tags__question__is_active=True)
            )
        ).order_by("-question_count")
    elif sorted_by == NAME:
        return tags.order_by("name")
    elif sorted_by == NEWEST:
        return tags.order_by("-created_at")
    return tags


def sort_user_tag(request, user_tags):
    sorted_by = request.query_params.get("sorted_by")
    if not (sorted_by in (VOTES, NAME)):
        return None
    if sorted_by == VOTES:
        return user_tags.order_by("-score")
    elif sorted_by == NAME:
        return user_tags.order_by("tag__name")
    return user_tags
