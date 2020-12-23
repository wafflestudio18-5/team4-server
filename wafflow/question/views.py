from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from question.models import Question, UserQuestion
from question.serializers import QuestionSerializer, AuthorOfQuestionSerializer, TagSerializer


class QuestionViewSet(viewsets.GenericViewSet):
    queryset = Question.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = QuestionSerializer

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'tag':
            return TagSerializer
        if self.action == 'user':
            return AuthorOfQuestionSerializer
        return self.serializer_class

    # POST /api/v1/question/
    def create(self, request):
        """Question 생성 API"""
        user = request.user
        print(user)
        print(1234)
        if not user:
            return Response({'error': "질문하려면 로그인이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save()

        return Response(self.get_serializer(question).data, status=status.HTTP_201_CREATED)

    # GET /api/v1/question/{question_id}/
    def retrieve(self, request, pk=None):
        """단일 Question 조회 API"""
        question = self.get_object()
        return Response(self.get_serializer(question).data)

    # GET /api/v1/question/search/keywords/?keywords={}&filter_by={}&sorted_by={}&page={}
    def list(self, request):
        """여러 Questions 조회 API"""
        queryset = self.get_queryset()
        keywords = self.request.query_params.get('keywords')
        filter_by = self.request.query_params.get('filter_by')
        sorted_by = self.request.query_params.get('sorted_by')
        page = self.request.query_params.get('page')

        if filter_by == "no_accepted_answer":
            queryset = queryset.filter(has_accepted=False)

        if sorted_by == "newest":
            queryset = queryset.order_by('-created_at')
        elif sorted_by == "recent_activity":
            queryset = queryset.order_by('-updated_at')
        elif sorted_by == "most_votes":
            queryset = queryset.order_by('-vote')
        else:
            queryset = queryset.order_by('most_frequent')

        return Response(self.get_serializer(queryset, many=True).data)

    # PUT /api/v1/question/{question_id}/
    def update(self, request, pk=None):
        """Question 수정 API"""
        user = request.user
        question = self.get_object()

        if not question.author == user:
            return Response({'error': "작성자만 Question을 수정할 수 있습니다."}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()
        if question.title == data.get('title'):
            data.pop('title')

        serializer = self.get_serializer(question, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(question, serializer.validated_data)
        return Response(serializer.data)

