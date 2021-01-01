from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from question.models import UserQuestion, Question, QuestionTag
from tag.models import UserTag
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
        user_question, created = UserQuestion.objects.get_or_create(
            user=user, question=question, defaults={"rating": 0}
        )

        rating = request.data.get("rating")
        if not rating:
            return Response(
                {"message": "Validation Error: Rating required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rating = int(rating)
        rating_diff = rating - user_question.rating
        question_tags = QuestionTag.objects.filter(question=question)
        for question_tag in question_tags:
            user_tag = UserTag.objects.get(user=question.user, tag=question_tag.tag)
            user_tag.score += rating_diff
            user_tag.save()
        question.vote += rating_diff
        user_question.rating = rating

        question.save()
        user_question.save()

        data = {
            "user_id": user.id,
            "question_id": question.id,
            "vote": question.vote,
            "rating": user_question.rating,
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
        user_answer, created = UserAnswer.objects.get_or_create(
            user=user, answer=answer, defaults={"rating": 0}
        )

        rating = request.data.get("rating")
        if not rating:
            return Response(
                {"message": "Validation Error: Rating required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rating = int(rating)
        rating_diff = rating - user_answer.rating
        question_tags = QuestionTag.objects.filter(question=answer.question)
        for question_tag in question_tags:
            user_tag = UserTag.objects.get(user=answer.user, tag=question_tag.tag)
            user_tag.score += rating_diff
            user_tag.save()
        answer.vote += rating_diff
        user_answer.rating = rating

        answer.save()
        user_answer.save()

        data = {
            "user_id": user.id,
            "answer_id": answer.id,
            "vote": answer.vote,
            "rating": user_answer.rating,
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
        user_comment, created = UserComment.objects.get_or_create(
            user=user, comment=comment, defaults={"rating": 0}
        )

        rating = request.data.get("rating")
        if not rating:
            return Response(
                {"message": "Validation Error: Rating required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rating = int(rating)
        comment.vote += rating - user_comment.rating
        user_comment.rating = rating

        comment.save()
        user_comment.save()

        data = {
            "user_id": user.id,
            "comment_id": comment.id,
            "vote": comment.vote,
            "rating": user_comment.rating,
        }
        return Response(data, status=status.HTTP_200_OK)
