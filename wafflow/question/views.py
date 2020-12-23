from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from question.constants import *
from question.models import Question, UserQuestion, Tag, QuestionTag
from question.serializers import QuestionSerializer, QuestionEditSerializer, QuestionProduceSerializer, QuestionUserSerializer


class QuestionViewSet(viewsets.GenericViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_permissions(self):
        if self.action in ("create", "update",):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    def get_serializer_class(self):
        if self.action in ("create",):
            return QuestionProduceSerializer
        elif self.action in ("update",):
            return QuestionEditSerializer
        else:
            return QuestionSerializer

    def create(self, request):
        """Question 생성 API"""
        user = request.user
        data = request.data.copy()
        if not user:
            return Response({'error': "질문하려면 로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)

        with transaction.atomic():
            question_serializer = self.get_serializer(data=data)
            question_serializer.is_valid(raise_exception=True)
            question = question_serializer.save()

            raw_tags = data.get('tags')
            tags = raw_tags.split('+') if raw_tags else None
            if tags:
                for tag in tags:
                    if not Tag.objects.filter(name=tag).exists():
                        tag = Tag.objects.create(name=tag)
                    else:
                        tag = Tag.objects.get(name=tag)
                    QuestionTag.objects.create(question=question, tag=tag)
        return Response(
            QuestionSerializer(question, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, pk=None):
        """단일 Question 조회 API"""
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response(
                {"message": "There is no question with the given ID"},
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
            return Response({'error': "작성자만 Question을 수정할 수 있습니다."}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()
        title = data.get("title")
        content = data.get("content")
        if not title or not content:
            return Response({'error': "제목과 본문은 필수적으로 입력해야 합니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.get_serializer(question, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(QuestionSerializer(question, context=self.get_serializer_context()).data)


class QuestionUserViewSet(viewsets.GenericViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionUserSerializer

    def get_permissions(self):
        return (AllowAny(),)

    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"message": "There is no user with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        sorted_by = request.query_params.get("sorted_by")
        if not (sorted_by in (VOTE, ACTIVITY, NEWEST, VIEW)):
            return Response(
                {
                    "message": "Invalid sorted_by. It must be one of votes, activity, newest"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        questions_all = Question.objects.filter(user=user, is_active=True)
        if sorted_by == VOTE:
            questions_all = questions_all.order_by("-vote")
        elif sorted_by == ACTIVITY:
            questions_all = questions_all.order_by("-updated_at")
        elif sorted_by == NEWEST:
            questions_all = questions_all.order_by("-created_at")
        elif sorted_by == VIEW:
            questions_all = questions_all.order_by("-view_count")

        page = int(request.query_params.get("page"))
        paginator = Paginator(questions_all, QUESTION_PER_PAGE)

        try:
            questions = paginator.page(page)
        except EmptyPage:
            return Response(
                {
                    f"message": f"Invalid page it must be between 1 and {paginator.num_pages}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(self.get_serializer(questions, many=True).data)
