from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage

from django.contrib.auth.models import User
from question.models import Question
from answer.models import Answer
from answer.constants import *
from answer.serializers import (
    AnswerSummarySerializer,
    AnswerInfoSerializer,
    AnswerEditSerializer,
    AnswerProduceSerializer,
    AnswerAcceptionSerializer,
)


class AnswerUserViewSet(viewsets.GenericViewSet):
    queryset = Answer.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = AnswerSummarySerializer

    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk, is_active=True)
        except User.DoesNotExist:
            return Response(
                {"message": "There is no user with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        sorted_by = request.query_params.get("sorted_by")

        if not (sorted_by in (VOTE, ACTIVITY, NEWEST)):
            return Response(
                {
                    "message": "Invalid sorted_by. It must be one of votes, activity, newest"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        answers_all = Answer.objects.filter(user=user, is_active=True)
        if sorted_by == VOTE:
            answers_all = answers_all.order_by("-vote")
        elif sorted_by == ACTIVITY:
            answers_all = answers_all.order_by("-updated_at")
        elif sorted_by == NEWEST:
            answers_all = answers_all.order_by("-created_at")

        page = request.query_params.get("page")

        if page is None:
            return Response(
                {f"message": f"there must be page"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        paginator = Paginator(answers_all, ANSWER_PER_PAGE)

        try:
            answers = paginator.page(page)
        except EmptyPage:
            return Response(
                {
                    f"message": f"Invalid page it must be between 1 and {paginator.num_pages}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"answers": AnswerSummarySerializer(answers, many=True).data})


class AnswerQuestionViewSet(viewsets.GenericViewSet):
    queryset = Answer.objects.all()

    def get_permissions(self):
        if self.action in ("make",):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    def get_serializer_class(self):
        if self.action in ("retrieve",):
            return AnswerInfoSerializer
        if self.action in ("make",):
            return AnswerProduceSerializer

    def retrieve(self, request, pk=None):
        try:
            question = Question.objects.get(pk=pk, is_active=True)
        except Question.DoesNotExist:
            return Response(
                {"message": "There is no question with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        sorted_by = request.query_params.get("sorted_by")

        if not (sorted_by in (VOTE, ACTIVITY, OLDEST)):
            return Response(
                {
                    "message": "Invalid sorted_by. It must be one of votes, activity, oldest"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        answers_all = Answer.objects.filter(question=question, is_active=True)
        if sorted_by == VOTE:
            answers_all = answers_all.order_by("-is_accepted", "-vote")
        elif sorted_by == ACTIVITY:
            answers_all = answers_all.order_by("-is_accepted", "-updated_at")
        elif sorted_by == OLDEST:
            answers_all = answers_all.order_by("-is_accepted", "created_at")

        page = request.query_params.get("page")

        if page is None:
            return Response(
                {f"message": f"there must be page"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        paginator = Paginator(answers_all, ANSWER_PER_PAGE)

        try:
            answers = paginator.page(page)
        except EmptyPage:
            return Response(
                {
                    f"message": f"Invalid page it must be between 1 and {paginator.num_pages}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"answers": self.get_serializer(answers, many=True).data})

    def make(self, request, pk=None):
        try:
            question = Question.objects.get(pk=pk, is_active=True)
        except Question.DoesNotExist:
            return Response(
                {"message": "There is no question with the given id"},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data["question_id"] = pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        answer = serializer.save()

        return Response(
            AnswerInfoSerializer(answer, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )


class AnswerViewSet(viewsets.GenericViewSet):
    queryset = Answer.objects.all()

    def get_permissions(self):
        if self.action in ("update", "destroy", "acception"):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    def get_serializer_class(self):
        if self.action in ("update",):
            return AnswerEditSerializer
        elif self.action in ("acception",):
            return AnswerAcceptionSerializer
        return AnswerInfoSerializer

    def retrieve(self, request, pk=None):
        try:
            answer = Answer.objects.get(pk=pk, is_active=True)
        except Answer.DoesNotExist:
            return Response(
                {"message": "There is no answer with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(self.get_serializer(answer).data)

    def update(self, request, pk=None):
        try:
            answer = Answer.objects.get(pk=pk, is_active=True)
        except Answer.DoesNotExist:
            return Response(
                {"message": "There is no answer with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user != answer.user:
            return Response(
                {"message": "Not allowed to edit this answer"},
                status=status.HTTP_403_FORBIDDEN,
            )

        content = request.data.get("content", "")
        if content != "":
            serializer = self.get_serializer(answer, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(
            AnswerInfoSerializer(answer, context=self.get_serializer_context()).data,
        )

    def destroy(self, request, pk=None):
        try:
            answer = Answer.objects.get(pk=pk)
        except Answer.DoesNotExist:
            return Response(
                {"message": "There is no answer with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not answer.is_active:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        if request.user != answer.user or answer.is_accepted:
            return Response(
                {"message": "Not allowed to delete this answer"},
                status=status.HTTP_403_FORBIDDEN,
            )

        answer.is_active = False
        answer.save()

        return Response({})

    @action(methods=["DELETE", "POST"], detail=True)
    def acception(self, request, pk=None):
        try:
            answer = Answer.objects.get(pk=pk, is_active=True)
        except Answer.DoesNotExist:
            return Response(
                {"message": "There is no answer with the given id"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user != answer.question.user:
            return Response(
                {"message": "Not allowed to change acception of this answer"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.method == "POST":
            return self.post_acception(request, answer)
        if request.method == "DELETE":
            return self.delete_acception(request, answer)

    def set_acception(self, answer, is_accepted):
        answer.is_accepted = is_accepted
        answer.save()
        question = answer.question
        question.has_accepted = is_accepted
        question.save()

        answer_user_profile = answer.user.profile
        question_user_profile = question.user.profile
        question_user_profile.reputation += 2 * (1 if is_accepted else -1)
        answer_user_profile.reputation += 15 * (1 if is_accepted else -1)
        answer_user_profile.save()
        question_user_profile.save()

    def post_acception(self, request, answer):
        if answer.question.has_accepted:
            return Response(
                {"message": "The question has already accepted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.set_acception(answer, True)

        return Response(self.get_serializer(answer).data, status=status.HTTP_200_OK)

    def delete_acception(self, request, answer):
        if not answer.is_accepted:
            return Response(
                {"message": "The answer is not accepted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.set_acception(answer, False)

        return Response(self.get_serializer(answer).data, status=status.HTTP_200_OK)
