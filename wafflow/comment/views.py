from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from answer.models import Answer
from comment.models import Comment
from comment.serializers import (
    CommentAnswerProduceSerializer,
    CommentEditSerializer,
    CommentSerializer,
    CommentQuestionProduceSerializer,
)
from question.models import Question


class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in (
            "update",
            "destroy",
        ):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    def retrieve(self, request, pk=None):
        comment = Comment.objects.filter(pk=pk, is_active=True).last()
        if not comment:
            return Response(
                {"error": "There is no comment with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(self.get_serializer(comment).data)

    def update(self, request, pk=None):
        comment = Comment.objects.filter(pk=pk, is_active=True).last()
        if not comment:
            return Response(
                {"message": "There is no comment with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.user != comment.user:
            return Response(
                {"message": "Not allowed to edit this comment"},
                status=status.HTTP_403_FORBIDDEN,
            )

        content = request.data.get("content", "")
        if content != "":
            serializer = CommentEditSerializer(comment, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(
            self.get_serializer(comment, context=self.get_serializer_context()).data,
        )

    def destroy(self, request, pk=None):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response(
                {"message": "There is no comment with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not comment.is_active:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        if request.user != comment.user:
            return Response(
                {"message": "Not allowed to delete this comment"},
                status=status.HTTP_403_FORBIDDEN,
            )
        comment.is_active = False
        comment.save()
        return Response({})


class CommentAnswerViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ("make",):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    def get_serializer_class(self):
        if self.action in ("retrieve",):
            return CommentSerializer
        if self.action in ("make",):
            return CommentAnswerProduceSerializer

    def retrieve(self, request, pk=None):
        answer = Answer.objects.filter(pk=pk, is_active=True)
        if not answer:
            return Response(
                {"message": "There is no answer with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )
        comments = Comment.objects.filter(answer=answer, is_active=True)
        return Response(self.get_serializer(comments, many=True).data)

    def make(self, request, pk=None):
        answer = Answer.objects.filter(pk=pk, is_active=True)
        if not answer:
            return Response(
                {"message": "There is no answer with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = request.data.copy()
        data["answer_id"] = pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        return Response(
            CommentSerializer(comment, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )


class CommentQuestionViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ("make",):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    def get_serializer_class(self):
        if self.action in ("retrieve",):
            return CommentSerializer
        if self.action in ("make",):
            return CommentQuestionProduceSerializer

    def retrieve(self, request, pk=None):
        question = Question.objects.filter(pk=pk, is_active=True)
        if not question:
            return Response(
                {"message": "There is no question with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )
        comments = Comment.objects.filter(question=question, is_active=True)
        return Response(self.get_serializer(comments, many=True).data)

    def make(self, request, pk=None):
        question = Question.objects.filter(pk=pk, is_active=True)
        if not question:
            return Response(
                {"message": "There is no question with the given ID"},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = request.data.copy()
        data["question_id"] = pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        return Response(
            CommentSerializer(comment, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )
