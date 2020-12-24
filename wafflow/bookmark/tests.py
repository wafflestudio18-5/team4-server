from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework import status
from django.utils import timezone
from rest_framework.authtoken.models import Token

from answer.models import Answer, UserAnswer
from comment.models import Comment
from question.models import Question, UserQuestion
from answer.tests import UserQuestionTestSetting

import json


class BookmarkTestCase(UserQuestionTestSetting):
    def assert_in_data(self, data):
        self.assertIn("user_id", data)
        self.assertIn("question_id", data)
        self.assertIn("bookmark_count", data)
        self.assertIn("bookmarked", data)

    def check_db_count(self, **kwargs):
        user_question = kwargs.get("user_question", 0)

        super().check_db_count()
        self.assertEqual(UserQuestion.objects.all().count(), user_question)


class PostBookmarkTestCase(BookmarkTestCase):
    client = Client()

    def setUp(self):
        self.set_up_user_question()

    def test_post_bookmark_question_question_id_invalid_token(self):
        question = Question.objects.get(title="Hello")

        response = self.client.post(f"/bookmark/question/{question.id}/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(
            f"/bookmark/question/{question.id}/", HTTP_AUTHORIZATION="asdf"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.check_db_count()

    def test_post_bookmark_question_question_id_invalid_id(self):
        question = Question.objects.get(title="Hello")

        response = self.client.post(
            f"/bookmark/question/-1/", HTTP_AUTHORIZATION=self.eldpswp99_token
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

    def test_post_bookmark_question_question_id_already_bookmarked(self):
        question = Question.objects.get(title="Hello")
        eldpswp99 = User.objects.get(username="eldpswp99")
        qwerty = User.objects.get(username="qwerty")
        user_question, created = UserQuestion.objects.get_or_create(
            user=eldpswp99, question=question, defaults={"rating": 0}
        )

        user_question.bookmark = True
        user_question.bookmark_at = timezone.now()
        user_question.save()

        response = self.client.post(
            f"/bookmark/question/{question.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            f"/bookmark/question/{question.id}/", HTTP_AUTHORIZATION=self.qwerty_token
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assert_in_data(data)
        self.assertEqual(data["user_id"], User.objects.get(username="qwerty").id)
        self.assertEqual(data["question_id"], question.id)
        self.assertEqual(data["bookmark_count"], 2)
        self.assertEqual(data["bookmarked"], True)
        user_question = UserQuestion.objects.get(user=eldpswp99, question=question)
        self.assertIsNotNone(user_question.bookmark_at)
        user_question = UserQuestion.objects.get(user=qwerty, question=question)
        self.assertIsNotNone(user_question.bookmark_at)
        self.check_db_count(user_question=2)

    def test_post_bookmark_question_question_id_twice(self):
        question = Question.objects.get(title="Hello")

        response = self.client.post(
            f"/bookmark/question/{question.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        eldpswp99 = User.objects.get(username="eldpswp99")
        user_question = UserQuestion.objects.get(user=eldpswp99, question=question)
        self.assertIsNotNone(user_question.bookmark_at)

        self.assert_in_data(data)
        self.assertEqual(data["user_id"], User.objects.get(username="eldpswp99").id)
        self.assertEqual(data["question_id"], question.id)
        self.assertEqual(data["bookmark_count"], 1)
        self.assertEqual(data["bookmarked"], True)

        response = self.client.post(
            f"/bookmark/question/{question.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        user_question = UserQuestion.objects.get(user=eldpswp99, question=question)
        self.assertIsNotNone(user_question.bookmark_at)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count(user_question=1)

    def test_post_bookmark_question_question_id(self):
        question = Question.objects.get(title="Hello")

        response = self.client.post(
            f"/bookmark/question/{question.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assert_in_data(data)
        self.assertEqual(data["user_id"], User.objects.get(username="eldpswp99").id)
        self.assertEqual(data["question_id"], question.id)
        self.assertEqual(data["bookmark_count"], 1)
        self.assertEqual(data["bookmarked"], True)

        eldpswp99 = User.objects.get(username="eldpswp99")
        user_question = UserQuestion.objects.get(user=eldpswp99, question=question)
        self.assertIsNotNone(user_question.bookmark_at)

        self.check_db_count(user_question=1)


class DeleteBookmarkTestCase(BookmarkTestCase):
    client = Client()

    def check_db_count(self, **kwargs):
        user_question = kwargs.get("user_question", 1)
        bookmark_count = kwargs.get("bookmark_count", 1)

        super().check_db_count(user_question=user_question)
        self.assertEqual(
            UserQuestion.objects.filter(
                bookmark=True, question__is_active=True
            ).count(),
            bookmark_count,
        )

    def setUp(self):
        self.set_up_user_question()
        question = Question.objects.get(title="Hello")
        eldpswp99 = User.objects.get(username="eldpswp99")
        user_question, created = UserQuestion.objects.get_or_create(
            user=eldpswp99, question=question, defaults={"rating": 0}
        )

        user_question.bookmark = True
        user_question.bookmark_at = timezone.now()
        user_question.save()

    def test_delete_bookmark_question_question_id_invalid_token(self):
        question = Question.objects.get(title="Hello")

        response = self.client.delete(f"/bookmark/question/{question.id}/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.delete(
            f"/bookmark/question/{question.id}/", HTTP_AUTHORIZATION="asdf"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.check_db_count()

    def test_delete_bookmark_question_question_id_invalid_id(self):
        question = Question.objects.get(title="Hello")

        response = self.client.delete(
            f"/bookmark/question/-1/", HTTP_AUTHORIZATION=self.eldpswp99_token
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

    def test_delete_bookmark_question_question_id_not_bookmarked(self):
        question = Question.objects.get(title="Hello")

        response = self.client.delete(
            f"/bookmark/question/{question.id}/", HTTP_AUTHORIZATION=self.qwerty_token
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        qwerty = User.objects.get(username="qwerty")
        user_question = UserQuestion.objects.get(user=qwerty, question=question)
        self.assertIsNone(user_question.bookmark_at)
        eldpswp99 = User.objects.get(username="eldpswp99")
        user_question = UserQuestion.objects.get(user=eldpswp99, question=question)
        self.assertIsNotNone(user_question.bookmark_at)

        data = response.data

        self.assert_in_data(data)
        self.assertEqual(data["user_id"], User.objects.get(username="qwerty").id)
        self.assertEqual(data["question_id"], question.id)
        self.assertEqual(data["bookmark_count"], 1)
        self.assertEqual(data["bookmarked"], False)
        self.check_db_count(user_question=2)

        response = self.client.delete(
            f"/bookmark/question/{question.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )
        eldpswp99 = User.objects.get(username="eldpswp99")
        user_question = UserQuestion.objects.get(user=eldpswp99, question=question)
        self.assertIsNone(user_question.bookmark_at)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assert_in_data(data)
        self.assertEqual(data["user_id"], User.objects.get(username="eldpswp99").id)
        self.assertEqual(data["question_id"], question.id)
        self.assertEqual(data["bookmark_count"], 0)
        self.assertEqual(data["bookmarked"], False)
        self.check_db_count(bookmark_count=0, user_question=2)

    def test_delete_bookmark_question_question_id_twice(self):
        question = Question.objects.get(title="Hello")

        response = self.client.delete(
            f"/bookmark/question/{question.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assert_in_data(data)
        self.assertEqual(data["user_id"], User.objects.get(username="eldpswp99").id)
        self.assertEqual(data["question_id"], question.id)
        self.assertEqual(data["bookmark_count"], 0)
        self.assertEqual(data["bookmarked"], False)

        self.check_db_count(bookmark_count=0)
        eldpswp99 = User.objects.get(username="eldpswp99")
        user_question = UserQuestion.objects.get(user=eldpswp99, question=question)
        self.assertIsNone(user_question.bookmark_at)

        response = self.client.delete(
            f"/bookmark/question/{question.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        data = response.data

        self.assert_in_data(data)
        self.assertEqual(data["user_id"], User.objects.get(username="eldpswp99").id)
        self.assertEqual(data["question_id"], question.id)
        self.assertEqual(data["bookmark_count"], 0)
        self.assertEqual(data["bookmarked"], False)

        user_question = UserQuestion.objects.get(user=eldpswp99, question=question)
        self.assertIsNone(user_question.bookmark_at)

        self.check_db_count(bookmark_count=0)

    def test_delete_bookmark_question_question_id(self):
        question = Question.objects.get(title="Hello")

        response = self.client.delete(
            f"/bookmark/question/{question.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assert_in_data(data)
        self.assertEqual(data["user_id"], User.objects.get(username="eldpswp99").id)
        self.assertEqual(data["question_id"], question.id)
        self.assertEqual(data["bookmark_count"], 0)
        self.assertEqual(data["bookmarked"], False)

        eldpswp99 = User.objects.get(username="eldpswp99")
        user_question = UserQuestion.objects.get(user=eldpswp99, question=question)
        self.assertIsNone(user_question.bookmark_at)
        self.check_db_count(bookmark_count=0)


class GetBookmarkUserMeTestCase:
    pass
