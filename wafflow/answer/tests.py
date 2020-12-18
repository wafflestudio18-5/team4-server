from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework import status

import json

from answer.models import Answer, UserAnswer
from user.models import UserProfile
from question.models import Question
from comment.models import Comment


class GetAnswerTestCase(TestCase):
    client = Client()
    ANSWER_COUNT = 3

    def create_answer(self, user, question, content):
        return Answer.objects.create({
            "user": user,
            "question": question,
            "content": content
        })

    def setUp(self):
        user = User.objects.create_user({
            "username": "eldpswp99",
            "email": "nrg1392@naver.com",
            "password": "password"
        })
        profile = UserProfile.objects.create({
            "user": user,
            "nickname": "MyungHoon Park",
            "intro": "Hello World!",
        })
        question = Question.objects.create({
            "user": user,
            "title": "Hello",
            "content": "World",
        })
        comment = Comment.objects.create({
            "user": user,
            "type": Comment.ANSWER,
            "content": "content"
        })

        for answer in range(self.ANSWER_COUNT):
            self.create_answer(user, question, "a" * (answer + 1))

    def test_get_answer_with_answer_id(self):
        response = self.client.get(
            f'/answer/1'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["id"], 1)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertEqual(data["content"], "a")
        self.assertEqual(data["vote"], 0)
        self.assertEqual(data["is_accepted"], False)
        self.assertEqual(data["rating"], 0)
        self.assertIsNotNone(data["author"])

        author = data["author"]
        self.assertIn("id", author)
        self.assertEqual(author["username"], "eldpswp99")
        self.assertIn("reputation", author)

        self.assertEqual(data["comment_count"], 0)

        self.assertEqual(Answer.objects.all().count(), 3)
        self.assertEqual(Question.objects.all().count(), 1)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(UserProfile.all().count(), 1)
