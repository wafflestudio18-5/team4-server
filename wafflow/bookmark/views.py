from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from question.models import UserQuestion, Question
from bookmark.serializers import SimpleBookmarkSerializer


class BookmarkViewSet(viewsets.GenericViewSet):
    queryset = UserQuestion.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SimpleBookmarkSerializer

    def make(self, request, pk=None):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
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
        user_question.save()

        return Response(self.get_serializer(user_question).data)

    def destroy(self, request, pk=None):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
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
        user_question.save()

        return Response(self.get_serializer(user_question).data)
