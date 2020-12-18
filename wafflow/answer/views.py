from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import redirect
from django.core.paginator import Paginator

from django.contrib.auth.models import User
from question.models import Question
from answer.models import Answer
from answer.constants import *
from answer.serializers import AnswerSummarySerializer, AnswerInfoSerializer


class AnswerUserViewSet(viewsets.GenericViewSet):
    queryset = Answer.objects.all()
    permission_classes = (AllowAny(),)
    serializer_class = AnswerSummarySerializer

    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"message": "There is no user with the given ID"},
                            status=status.HTTP_404_NOT_FOUND)

        sorted_by = request.query_params.get("sorted_by")

        if not (sorted_by in (VOTE, ACTIVITY, NEWEST)):
            return Response({"message": "Invalid sorted_by. It must be one of votes, activity, newest"},
                            status=status.HTTP_400_BAD_REQUEST)

        answers_all = Answer.objects.filter(user=user)
        if sorted_by == VOTE:
            answers_all.order_by("-vote")
        elif sorted_by == ACTIVITY:
            answers_all.order_by("-updated_at")
        elif sorted_by == NEWEST:
            answers_all.order_by("-created_at")

        page = request.query_params.get("page")
        paginator = Paginator(answers_all, ANSWER_PER_PAGE)
        if page is None or page < 1:
            return redirect(f'/answer/user/{pk}/?sorted_by={sorted_by}&page=1', permanent=True)
        elif page > paginator.num_pages:
            return redirect(f'/answer/user/{pk}/?sorted_by={sorted_by}&page={paginator.num_pages}', permanent=True)

        answers = paginator.page(page)

        return Response({
            "answers": AnswerSummarySerializer(answers, many=True).data
        })


class AnswerQuestionViewSet(viewsets.GenericViewSet):
    queryset = Answer.objects.all()
    permission_classes = (AllowAny(),)
    serializer_class = AnswerInfoSerializer

    def get_permissions(self):
        if self.action in ('make',):
            return IsAuthenticated()
        return AllowAny()

    def retrieve(self, request, pk=None):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"message": "There is no question with the given ID"},
                            status=status.HTTP_404_NOT_FOUND)

        sorted_by = request.query_params.get("sorted_by")

        if not (sorted_by in (VOTE, ACTIVITY, OLDEST)):
            return Response({"message": "Invalid sorted_by. It must be one of votes, activity, oldest"},
                            status=status.HTTP_400_BAD_REQUEST)

        answers_all = Answer.objects.filter(question=question)
        if sorted_by == VOTE:
            answers_all.order_by("-vote")
        elif sorted_by == ACTIVITY:
            answers_all.order_by("-updated_at")
        elif sorted_by == OLDEST:
            answers_all.order_by("created_at")

        page = request.query_params.get("page")
        paginator = Paginator(answers_all, ANSWER_PER_PAGE)
        if page is None or page < 1:
            return redirect(f'/answer/question/{pk}/?sorted_by={sorted_by}&page=1', permanent=True)
        elif page > paginator.num_pages:
            return redirect(f'/answer/question/{pk}/?sorted_by={sorted_by}&page={paginator.num_pages}', permanent=True)

        answers = paginator.page(page)

        return Response({
            "answers": AnswerSummarySerializer(answers, many=True).data
        })

    def make(self, request, pk=None):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"message": "There is no question with the given id"},
                            status=status.HTTP_404_NOT_FOUND)
        data = request.data
        serializer = self.get_serializer()


class AnswerViewSet(viewsets.GenericViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerInfoSerializer

    def get_permissions(self):
        if self.action in ("retrieve", "update", "destroy"):
            return IsAuthenticated()
        return AllowAny()

    def retrieve(self, request, pk=None):
        try:
            answer = Answer.objects.get(pk=pk)
        except Answer.DoesNotExist:
            return Response({"message": "There is no answer with the given ID"},
                            status=status.HTTP_404_NOT_FOUND)

        return Response(self.get_serializer(answer).data)

    def update(self, request, pk=None):
        try:
            answer = Answer.objects.get(pk=pk)
        except Answer.DoesNotExist:
            return Response({"message": "There is no answer with the given ID"},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(answer, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(self.get_serializer(answer).data)

    def delete(self, request, pk=None):
        try:
            answer = Answer.objects.get(pk=pk)
        except Answer.DoesNotExist:
            return Response({"message": "There is no answer with the given ID"},
                            status=status.HTTP_404_NOT_FOUND)
        if not answer.is_active:
            return Response({"message": "Validation Error: already deleted"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(answer, {"is_active": False}, partial=True)
        serializer.is_valid()
        serializer.save()

        return Response({})
