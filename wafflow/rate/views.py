from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from question.models import UserQuestion, Question
from answer.models import UserAnswer, Answer
from comment.models import UserComment, Comment


class RateViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated(), )

    def get_permissions(self):
        return self.permission_classes
    
    # PUT /rate/question/{question_id}
    def rate_question(self, request, pk=None):
        user = request.user
        try:
            question = Question.objects.get_object_or_404(id=pk)
        except Question.DoesNotExist:
            return Response(
                {"message": "There is no question with the id"}, status=status.HTTP_404_NOT_FOUND,
            )
        userquestion = user.user_questions.objects.get(question=question)
        
        rating = request.data.get('rating')
        question.vote += rating - userquestion.rating
        userquestion.rating = rating

        data = {
            "user_id": user.id,
            "question_id": question.id,
            "vote": question.vote,
            "rating": rating
        }
        return Response(data, status=status.HTTP_200_OK)

    # PUT /rate/answer/{answer_id}
    def rate_answer(self, request, pk=None):
        user = request.user
        try:
            answer = Answer.objects.get_object_or_404(id=pk)
        except Answer.DoesNotExist:
            return Response(
                {"message": "There is no answer with the id"}, status=status.HTTP_404_NOT_FOUND,
            )
        useranswer = user.user_answers.objects.get(answer=answer)
        
        rating = request.data.get('rating')
        answer.vote += rating - useranswer.rating
        useranswer.rating = rating

        data = {
            "user_id": user.id,
            "answer_id": answer.id,
            "vote": answer.vote,
            "rating": rating
        }
        return Response(data, status=status.HTTP_200_OK)   

    # PUT /rate/comment/{comment_id}
    def rate_comment(self, request, pk=None):
        user = request.user
        try:
            comment = Comment.objects.get_object_or_404(id=pk)
        except Comment.DoesNotExist:
            return Response(
                {"message": "There is no comment with the id"}, status=status.HTTP_404_NOT_FOUND,
            )
        usercomment = user.user_comments.objects.get(comment=comment)
        
        rating = request.data.get('rating')
        comment.vote += rating - usercomment.rating
        usercomment.rating = rating

        data = {
            "user_id": user.id,
            "comment_id": comment.id,
            "vote": comment.vote,
            "rating": rating
        }
        return Response(data, status=status.HTTP_200_OK)