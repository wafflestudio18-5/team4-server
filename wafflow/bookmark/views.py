from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User

from question.models import UserQuestion, Question
from bookmark.serializers import SimpleBookmarkSerializer, BookmarkQuestionSerializer
from bookmark.constants import *


class BookmarkQuestionViewSet(viewsets.GenericViewSet):
    queryset = UserQuestion.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SimpleBookmarkSerializer

    def make(self, request, pk=None):
        try:
            question = Question.objects.get(pk=pk, is_active=True)
        except (Question.DoesNotExist, ValueError):
            return Response(
                {"message": "There is no question with the id"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = request.user
        user_question, created = UserQuestion.objects.get_or_create(
            user=user, question=question, defaults={"rating": 0}
        )

        if user_question.bookmark:
            return Response(
                {"message": "Validation Error: already bookmarked"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_question.bookmark = True
        user_question.bookmark_at = timezone.now()
        user_question.save()

        return Response(self.get_serializer(user_question).data)

    def destroy(self, request, pk=None):
        try:
            question = Question.objects.get(pk=pk, is_active=True)
        except (Question.DoesNotExist, ValueError):
            return Response(
                {"message": "There is no question with the id"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = request.user
        user_question, created = UserQuestion.objects.get_or_create(
            user=user, question=question, defaults={"rating": 0}
        )

        if not user_question.bookmark:
            return Response(
                self.get_serializer(user_question).data,
                status=status.HTTP_204_NO_CONTENT,
            )

        user_question.bookmark = False
        user_question.bookmark_at = None
        user_question.save()

        return Response(self.get_serializer(user_question).data)


class BookmarkUserViewSet(viewsets.GenericViewSet):
    queryset = UserQuestion.objects.all()
    permission_classes = (AllowAny,)

    def sorted_by_queryset(self, user_questions, sorted_by):
        queryset = {
            VOTE: user_questions.order_by("-question__vote"),
            ACTIVITY: user_questions.order_by("-question__updated_at"),
            NEWEST: user_questions.order_by("-question__created_at"),
            ADDED: user_questions.order_by("-bookmark_at"),
            VIEWS: user_questions.order_by("-question__view_count"),
        }
        return queryset.get(sorted_by)

    def retrieve(self, request, pk=None):
        if pk != "me":
            try:
                user = User.objects.get(pk=pk, is_active=True)
            except (User.DoesNotExist, ValueError):
                return Response(
                    {"message": "There is no user with this id"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            if not request.user.is_authenticated or not request.user.is_active:
                return Response(
                    {"message": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
                )
            user = request.user

        sorted_by = request.query_params.get("sorted_by")
        page = request.query_params.get("page")

        if not (sorted_by in (VOTE, ACTIVITY, NEWEST, ADDED, VIEWS)) or page is None:
            return Response(
                {"message": "Invalid sorted_by or page"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        page = int(page)
        user_questions_all = UserQuestion.objects.filter(
            user=user, bookmark=True, question__is_active=True
        )

        user_questions_all = self.sorted_by_queryset(user_questions_all, sorted_by)
        paginator = Paginator(user_questions_all, BOOKMARK_PER_PAGE)

        try:
            user_questions = paginator.page(page)
            questions = list(
                map(lambda user_question: user_question.question, user_questions)
            )
        except EmptyPage:
            return Response(
                {
                    f"message": f"Invalid page it must be between 1 and {paginator.num_pages}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"questions": BookmarkQuestionSerializer(questions, many=True).data}
        )
