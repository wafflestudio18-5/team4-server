from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from question.models import Question, UserQuestion, Tag, QuestionTag
from question.serializers import QuestionSerializer, QuestionEditSerializer, QuestionProduceSerializer


class QuestionViewSet(viewsets.GenericViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "destroy", "acception"):
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
            if not tags:
                return Response({'error': "최소한 하나의 태그를 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)
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
