from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from question.models import UserQuestion, Question
from answer.models import UserAnswer, Answer
from comment.models import UserComment, Comment


class RateViewSet(viewsets.GenericViewSet):
    @api_view(("PUT",))
    def rate_question(request, pk):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"message": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            question = Question.objects.get(id=pk, is_active=True)
        except Question.DoesNotExist:
            return Response(
                {"message": "There is no question with the id"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if question.user == user:
            return Response(
                {"message": "Not allowed to rate this question"},
                status=status.HTTP_403_FORBIDDEN,
            )
        userquestion, created = UserQuestion.objects.get_or_create(
            user=user, question=question, defaults={"rating": 0}
        )

        rating = request.data.get("rating")
        if not rating:
            return Response(
                {"message": "Validation Error: Rating required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rating = int(rating)
        question.vote += rating - userquestion.rating
        userquestion.rating = rating

        question.save()
        userquestion.save()

        data = {
            "user_id": user.id,
            "question_id": question.id,
            "vote": question.vote,
            "rating": userquestion.rating,
        }
        return Response(data, status=status.HTTP_200_OK)

    @api_view(("PUT",))
    def rate_answer(request, pk):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"message": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            answer = Answer.objects.get(id=pk, is_active=True)
        except Answer.DoesNotExist:
            return Response(
                {"message": "There is no answer with the id"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if answer.user == user:
            return Response(
                {"message": "Not allowed to rate this answer"},
                status=status.HTTP_403_FORBIDDEN,
            )
        useranswer, created = UserAnswer.objects.get_or_create(
            user=user, answer=answer, defaults={"rating": 0}
        )

        rating = request.data.get("rating")
        if not rating:
            return Response(
                {"message": "Validation Error: Rating required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rating = int(rating)
        answer.vote += rating - useranswer.rating
        useranswer.rating = rating

        answer.save()
        useranswer.save()

        data = {
            "user_id": user.id,
            "answer_id": answer.id,
            "vote": answer.vote,
            "rating": useranswer.rating,
        }
        return Response(data, status=status.HTTP_200_OK)

    @api_view(("PUT",))
    def rate_comment(request, pk):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"message": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            comment = Comment.objects.get(id=pk, is_active=True)
        except Comment.DoesNotExist:
            return Response(
                {"message": "There is no comment with the id"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if comment.user == user:
            return Response(
                {"message": "Not allowed to rate this comment"},
                status=status.HTTP_403_FORBIDDEN,
            )
        usercomment, created = UserComment.objects.get_or_create(
            user=user, comment=comment, defaults={"rating": 0}
        )

        rating = request.data.get("rating")
        if not rating:
            return Response(
                {"message": "Validation Error: Rating required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rating = int(rating)
        comment.vote += rating - usercomment.rating
        usercomment.rating = rating

        comment.save()
        usercomment.save()

        data = {
            "user_id": user.id,
            "comment_id": comment.id,
            "vote": comment.vote,
            "rating": usercomment.rating,
        }
        return Response(data, status=status.HTTP_200_OK)
