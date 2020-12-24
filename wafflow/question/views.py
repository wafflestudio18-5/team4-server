import operator
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Q
from functools import reduce
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from question.constants import *
from question.models import Question, Tag, QuestionTag
from question.serializers import (
    QuestionSerializer,
    QuestionEditSerializer,
    QuestionProduceSerializer,
    QuestionUserSerializer,
    QuestionTagSearchSerializer,
)


class QuestionViewSet(viewsets.GenericViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_permissions(self):
        if self.action in (
            "create",
            "update",
        ):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    def get_serializer_class(self):
        if self.action in ("create",):
            return QuestionProduceSerializer
        elif self.action in ("update",):
            return QuestionEditSerializer
        elif self.action in (
            "tagged",
            "search",
        ):
            return QuestionTagSearchSerializer
        else:
            return QuestionSerializer

    def create(self, request):
        """Question 생성 API"""
        user = request.user
        data = request.data.copy()
        if not user:
            return Response(
                {"error": "질문하려면 로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED
            )

        with transaction.atomic():
            question_serializer = self.get_serializer(data=data)
            question_serializer.is_valid(raise_exception=True)
            question = question_serializer.save()

            raw_tags = data.get("tags")
            tags = raw_tags.split("+") if raw_tags else None
            if tags:
                for tag in tags:
                    if not Tag.objects.filter(name=tag).exists():
                        tag = Tag.objects.create(name=tag)
                    else:
                        tag = Tag.objects.get(name=tag)
                    QuestionTag.objects.create(question=question, tag=tag)
            user_profile = user.profile
            user_profile.reputation += 40
            user_profile.save()
        return Response(
            QuestionSerializer(question, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None):
        """단일 Question 조회 API"""
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response(
                {"error": "There is no question with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )
        question.view_count += 1
        question.save()
        return Response(self.get_serializer(question).data)

    def update(self, request, pk=None):
        """Question 수정 API"""
        user = request.user
        question = self.get_object()
        if not question.user == user:
            return Response(
                {"error": "작성자만 Question을 수정할 수 있습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        data = request.data.copy()
        title = data.get("title")
        content = data.get("content")
        if not title or not content:
            return Response(
                {"error": "제목과 본문은 필수적으로 입력해야 합니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            serializer = self.get_serializer(question, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(
            QuestionSerializer(question, context=self.get_serializer_context()).data
        )

    @action(detail=False, methods=["GET"])
    def tagged(self, request):
        tags = request.query_params.get("tags")
        filter_by = request.query_params.get("filter_by")

        tags = tags.split(" ") if tags else None
        tags = Tag.objects.filter(name__in=tags).all()
        question_tags = [tag.question_tags.all() for tag in tags]
        questions_id = list(
            set(
                [
                    question.question_id
                    for question_tag in question_tags
                    for question in question_tag
                ]
            )
        )
        questions = Question.objects.filter(is_active=True, id__in=questions_id).all()

        # FIXME : filter_by 구현할 것.

        sorted_questions = sort_questions(request, questions)
        if sorted_questions is None:
            return Response(
                {"error": "Invalid sorted_by."}, status=status.HTTP_404_NOT_FOUND
            )
        paginated_questions = paginate_questions(request, sorted_questions)
        if paginated_questions is None:
            return Response(
                {"error": "Invalid page"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(self.get_serializer(paginated_questions, many=True).data)

    @action(detail=False, methods=["GET"])
    def search(self, request):
        keywords = request.query_params.get("keywords")
        filter_by = request.query_params.get("filter_by")

        keywords = keywords.split(" ") if keywords else None
        questions = Question.objects.filter(
            reduce(
                operator.and_, (Q(content__icontains=keyword) for keyword in keywords)
            )
        )

        # FIXME : filter_by 구현할 것.

        sorted_questions = sort_questions(request, questions)
        if sorted_questions is None:
            return Response(
                {"error": "Invalid sorted_by."}, status=status.HTTP_404_NOT_FOUND
            )
        paginated_questions = paginate_questions(request, sorted_questions)
        if paginated_questions is None:
            return Response(
                {"error": "Invalid page"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(self.get_serializer(paginated_questions, many=True).data)


class QuestionUserViewSet(viewsets.GenericViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionUserSerializer

    def get_permissions(self):
        return (AllowAny(),)

    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None
        questions = Question.objects.filter(user=user, is_active=True)

        sorted_user_questions = sort_user_questions(request, questions)
        if sorted_user_questions is None:
            return Response(
                {"error": "Invalid sorted_by."}, status=status.HTTP_404_NOT_FOUND
            )
        paginated_questions = paginate_questions(request, sorted_user_questions)
        if paginated_questions is None:
            return Response(
                {"error": "Invalid page"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(self.get_serializer(paginated_questions, many=True).data)


def sort_questions(request, questions):
    sorted_by = request.query_params.get("sorted_by")
    if not (sorted_by in (NEWEST, RECENT_ACTIVITY, MOST_VOTES, MOST_FREQUENT)):
        return None
    if sorted_by == NEWEST:
        questions = questions.order_by("-created_at")
    elif sorted_by == RECENT_ACTIVITY:
        questions = questions.order_by("-updated_at")
    elif sorted_by == MOST_VOTES:
        questions = questions.order_by("-vote")
    elif sorted_by == MOST_FREQUENT:
        questions = questions.order_by("-view_count")
    return questions


def sort_user_questions(request, questions):
    sorted_by = request.query_params.get("sorted_by")
    if not (sorted_by in (VOTES, ACTIVITY, NEWEST, VIEWS)):
        return None
    if sorted_by == VOTES:
        questions = questions.order_by("-vote")
    elif sorted_by == ACTIVITY:
        questions = questions.order_by("-updated_at")
    elif sorted_by == NEWEST:
        questions = questions.order_by("-created_at")
    elif sorted_by == VIEWS:
        questions = questions.order_by("-view_count")
    return questions


def paginate_questions(request, questions):
    page = int(request.query_params.get("page"))
    paginator = Paginator(questions, QUESTION_PER_PAGE)
    try:
        questions = paginator.page(page)
    except EmptyPage:
        return None
    return questions
