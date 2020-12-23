from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from question.models import UserQuestion, Question
from answer.models import UserAnswer, Answer
from comment.models import UserComment, Comment


class RateViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        return self.permission_classes

    # PUT /rate/question/{question_id}
    @api_view(("PUT",))
    def rate_question(request, pk):
        user = request.user
        try:
            question = Question.objects.get(id=pk)
        except Question.DoesNotExist:
            return Response(
                {"message": "There is no question with the id"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            userquestion = user.user_questions.get(question=question)
        except:
            userquestion = UserQuestion.objects.create(
                user=user, question=question, rating=UserQuestion.NONE
            )

        rating = int(request.data.get("rating"))
        question.vote += rating - userquestion.rating
        userquestion.rating = rating

        data = {
            "user_id": user.id,
            "question_id": question.id,
            "vote": question.vote,
            "rating": rating,
        }
        return Response(data, status=status.HTTP_200_OK)

    # PUT /rate/answer/{answer_id}
    @api_view(("PUT",))
    def rate_answer(request, pk):
        user = request.user
        try:
            answer = Answer.objects.get(id=pk)
        except Answer.DoesNotExist:
            return Response(
                {"message": "There is no answer with the id"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            useranswer = user.user_answers.get(answer=answer)
        except:
            useranswer = UserAnswer.objects.create(
                user=user, answer=answer, rating=UserAnswer.NONE
            )

        rating = int(request.data.get("rating"))
        answer.vote += rating - useranswer.rating
        useranswer.rating = rating

        data = {
            "user_id": user.id,
            "answer_id": answer.id,
            "vote": answer.vote,
            "rating": rating,
        }
        return Response(data, status=status.HTTP_200_OK)

    # PUT /rate/comment/{comment_id}
    @api_view(("PUT",))
    def rate_comment(request, pk):
        user = request.user
        try:
            comment = Comment.objects.get(id=pk)
        except Comment.DoesNotExist:
            return Response(
                {"message": "There is no comment with the id"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            usercomment = user.user_comments.get(comment=comment)
        except:
            usercomment = UserComment.objects.create(
                user=user, comment=comment, rating=UserComment.NONE
            )

        rating = int(request.data.get("rating"))
        comment.vote += rating - usercomment.rating
        usercomment.rating = rating

        data = {
            "user_id": user.id,
            "comment_id": comment.id,
            "vote": comment.vote,
            "rating": rating,
        }
        return Response(data, status=status.HTTP_200_OK)
