from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework import status
from django.utils import timezone
from rest_framework.authtoken.models import Token

from bookmark.constants import *
from answer.models import Answer, UserAnswer
from comment.models import Comment
from question.models import Question, UserQuestion, Tag, QuestionTag
from answer.tests import UserQuestionTestSetting

import json


class BookmarkTestCase(UserQuestionTestSetting):
    def assert_in_data(self, data):
        self.assertIn("user_id", data)
        self.assertIn("question_id", data)
        self.assertIn("bookmark_count", data)
        self.assertIn("bookmarked", data)

    def check_db_count(self, **kwargs):
        user_question_count = kwargs.get("user_question_count", 0)

        super().check_db_count()
        self.assertEqual(UserQuestion.objects.all().count(), user_question_count)


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

    def test_post_bookmark_question_question_id_deleted_question(self):
        question = Question.objects.get(title="Hello")
        question.is_active = False
        question.save()

        response = self.client.post(
            f"/bookmark/question/{question.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
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
        self.check_db_count(user_question_count=2)

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
        self.check_db_count(user_question_count=1)

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

        self.check_db_count(user_question_count=1)


class DeleteBookmarkTestCase(BookmarkTestCase):
    client = Client()

    def check_db_count(self, **kwargs):
        user_question_count = kwargs.get("user_question_count", 1)
        bookmark_count = kwargs.get("bookmark_count", 1)

        super().check_db_count(user_question=user_question_count)
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

    def test_delete_bookmark_question_question_id_deleted_question(self):
        question = Question.objects.get(title="Hello")
        question.is_active = False
        question.save()

        response = self.client.delete(
            f"/bookmark/question/{question.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
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
        self.check_db_count(user_question_count=2)

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
        self.check_db_count(bookmark_count=0, user_question_count=2)

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


class GetBookmarkUserMeTestCase(UserQuestionTestSetting):
    client = Client()
    WHOLE_QUESTION_COUNT = 46
    QUESTION_COUNT = 44

    def bookmark(self, user, question):
        user_question, created = UserQuestion.objects.get_or_create(
            user=user, question=question, defaults={"rating": 0}
        )
        user_question.bookmark = True
        user_question.bookmark_at = timezone.now()
        user_question.save()

    def setUp(self):
        self.set_up_user_question()

        eldpswp99 = User.objects.get(username="eldpswp99")
        qwerty = User.objects.get(username="qwerty")
        for loop_count in range(self.QUESTION_COUNT):
            question = Question.objects.create(
                user=eldpswp99,
                title=str(loop_count + 1),
                content=str(100 - (loop_count + 1)),
                view_count=str(100 - (loop_count + 1)),
                vote=loop_count + 1,
            )
            self.bookmark(qwerty, question)

        question = Question.objects.create(
            user=eldpswp99,
            title=str(-1),
            content=str(-1),
        )
        self.bookmark(qwerty, question)

        question.is_active = False
        question.save()
        self.ANSWSER_VIEW_COUNT = 100 - self.QUESTION_COUNT
        question = Question.objects.get(view_count=self.ANSWSER_VIEW_COUNT)
        answer = Answer.objects.create(
            user=eldpswp99, question=question, content="Hello"
        )
        self.bookmark(eldpswp99, question)
        answer.is_accepted = True
        answer.save()
        question.has_accepted = True
        question.save()
        tag = Tag.objects.create(name="django")
        QuestionTag.objects.create(question=question, tag=tag)

    def test_get_bookmark_user_me_invalid_token(self):
        resopnse = self.client.get(f"/bookmark/user/me/sorted_by=votes&page=1")
        self.assertEqual(resopnse.status_code, status.HTTP_401_UNAUTHORIZED)

        resopnse = self.client.get(
            f"/bookmark/user/me/sorted_by=votes&page=1", HTTP_AUTHORIZATION="asf"
        )
        self.assertEqual(resopnse.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_bookmark_user_me_invalid_page(self):
        resopnse = self.client.get(
            f"/bookmark/user/me/sorted_by=votes&page=-1",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )
        self.assertEqual(resopnse.status_code, status.HTTP_400_BAD_REQUEST)

        resopnse = self.client.get(
            f"/bookmark/user/me/sorted_by=votes&page=9999",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )
        self.assertEqual(resopnse.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_bookmark_user_me_invalid_sorted_by(self):
        resopnse = self.client.get(
            f"/bookmark/user/me/sorted_by=asfd&page=1",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )
        self.assertEqual(resopnse.status_code, status.HTTP_400_BAD_REQUEST)

        resopnse = self.client.get(
            f"/bookmark/user/me/&page=1", HTTP_AUTHORIZATION=self.eldpswp99_token
        )
        self.assertEqual(resopnse.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_bookmark_user_me_blank_bookmark(self):
        response = self.client.get(
            f"/bookmark/user/me/sorted_by_votes&page=1",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data["questions"])
        self.assertEqual(len(data["questions"]), 0)

    def assert_in_question(self, question):
        self.assertIn("id", question)
        self.assertIn("created_at", question)
        self.assertIn("updated_at", question)
        self.assertIn("title", question)
        self.assertIn("vote", question)
        self.assertIn("view_count", question)
        self.assertIn("answer_count", question)
        self.assertIn("bookmark_count", question)
        self.assertIn("has_accepted", question)
        self.assertIn("author", question)
        self.assertIn("tags", question)

        self.assertIsNotNone(question["author"])
        self.assertIsNotNone(question["tags"])
        author = question["author"]
        tags = question["tags"]
        self.assertIn("id", author)
        self.assertIn("username", author)
        self.assertIn("reputation", author)
        self.assertIn("picture", author)

        for tag in tags:
            self.assert_in_tag(tag)

    def assert_in_tag(self, tag):
        self.assertIn("id", tag)
        self.assertIn("name", tag)

    def assert_equal_question(self, question, vote, view_count):
        self.assert_in_question(question)
        self.assertEqual(question["title"], vote if vote != 0 else "Hello")
        self.assertEqual(question["vote"], vote)
        self.assertEqual(question["view_count"], view_count if vote != 0 else 0)
        self.assertEqual(
            question["answer_count"], 1 if view_count == self.ANSWSER_VIEW_COUNT else 0
        )
        self.assertEqual(
            question["bookmark_count"],
            2 if view_count == self.ANSWSER_VIEW_COUNT else 1,
        )
        self.assertEqual(
            question["has_accepted"],
            True if view_count == self.ANSWSER_VIEW_COUNT else False,
        )
        author = question["author"]
        self.assertEqual(author["username"], "eldpswp99")
        self.assertEqual(author["reputation"], 0)
        self.assertEqual(
            len(question["tags"]), 1 if view_count == self.ANSWSER_VIEW_COUNT else 0
        )

        if view_count == self.ANSWSER_VIEW_COUNT:
            tag = question["tags"][0]
            self.assertEqual(tag["name"], "django")

    def test_get_bookmark_user_me_sorted_by_votes(self):
        response = self.client.get(
            f"/bookmark/user/me/?sorted_by=votes&page=1",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data["questions"])
        self.assertEqual(len(data["questions"]), BOOKMARK_PER_PAGE)
        questions = data["questions"]
        view_count = 100 - self.QUESTION_COUNT
        vote = self.QUESTION_COUNT

        for question in questions:
            self.assert_equal_question(question, vote, view_count)
            view_count += 1
            vote -= 1

        response = self.client.get(
            f"/bookmark/user/me/?sorted_by=votes&page=2",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data["questions"])
        self.assertEqual(
            len(data["questions"]), self.QUESTION_COUNT - self.BOOKMARK_PER_PAGE
        )
        questions = data["questions"]

        for question in questions:
            self.assert_equal_question(question, vote, view_count)
            view_count += 1
            vote -= 1

    def test_get_bookmark_user_me_sorted_by_activity(self):
        CHANGE_QUESTION_VOTE = 38
        question = Question.objects.get(vote=CHANGE_QUESTION_VOTE)
        question.title = "changed"
        question.save()

        response = self.client.get(
            f"/bookmark/user/me/?sorted_by=activity&page=1",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data["questions"])
        self.assertEqual(len(data["questions"]), BOOKMARK_PER_PAGE)
        questions = data["questions"]
        view_count = 100 - self.QUESTION_COUNT
        vote = self.QUESTION_COUNT
        idx = 0

        for question in questions:
            if idx == 0:
                self.assert_equal_question(
                    question, CHANGE_QUESTION_VOTE, 100 - CHANGE_QUESTION_VOTE
                )
            else:
                self.assert_equal_question(question, vote, view_count)
                view_count += 1
                vote -= 1

            idx += 1
            if CHANGE_QUESTION_VOTE == vote:
                view_count += 1
                vote -= 1

        response = self.client.get(
            f"/bookmark/user/me/?sorted_by=activity&page=2",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data["questions"])
        self.assertEqual(
            len(data["questions"]), self.QUESTION_COUNT - self.BOOKMARK_PER_PAGE
        )
        questions = data["questions"]

        for question in questions:
            self.assert_equal_question(question, vote, view_count)
            view_count += 1
            vote -= 1

    def test_get_bookmark_user_me_sorted_by_newest(self):
        response = self.client.get(
            f"/bookmark/user/me/?sorted_by=newest&page=1",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        question = Question.objects.get(title="Hello")
        qwerty = User.objects.get(username="qwerty")
        self.bookmark(qwerty, question)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data["questions"])
        self.assertEqual(len(data["questions"]), BOOKMARK_PER_PAGE)
        questions = data["questions"]
        view_count = 100 - self.QUESTION_COUNT
        vote = self.QUESTION_COUNT

        for question in questions:
            self.assert_equal_question(question, vote, view_count)
            view_count += 1
            vote -= 1

        response = self.client.get(
            f"/bookmark/user/me/?sorted_by=newest&page=2",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data["questions"])
        self.assertEqual(
            len(data["questions"]), 1 + self.QUESTION_COUNT - self.BOOKMARK_PER_PAGE
        )
        questions = data["questions"]

        for question in questions:
            self.assert_equal_question(question, vote, view_count)
            view_count += 1
            vote -= 1

    def test_get_bookmark_user_me_sorted_by_view_count(self):
        response = self.client.get(
            f"/bookmark/user/me/?sorted_by=view_count&page=1",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data["questions"])
        self.assertEqual(len(data["questions"]), BOOKMARK_PER_PAGE)
        questions = data["questions"]
        view_count = 99
        vote = 100 - view_count

        for question in questions:
            self.assert_equal_question(question, vote, view_count)
            view_count -= 1
            vote += 1

        response = self.client.get(
            f"/bookmark/user/me/?sorted_by=view_count&page=2",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data["questions"])
        self.assertEqual(
            len(data["questions"]), self.QUESTION_COUNT - self.BOOKMARK_PER_PAGE
        )
        questions = data["questions"]

        for question in questions:
            self.assert_equal_question(question, vote, view_count)
            view_count -= 1
            vote += 1

    def test_get_bookmark_user_me_sorted_by_added(self):
        response = self.client.get(
            f"/bookmark/user/me/?sorted_by=added&page=1",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        question = Question.objects.get(title="Hello")
        qwerty = User.objects.get(username="qwerty")
        self.bookmark(qwerty, question)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data["questions"])
        self.assertEqual(len(data["questions"]), BOOKMARK_PER_PAGE)
        questions = data["questions"]
        view_count = 0
        vote = 0

        for question in questions:
            self.assert_equal_question(question, vote, view_count)
            if vote != 0:
                view_count += 1
                vote -= 1
            else:
                view_count = 100 - self.QUESTION_COUNT
                vote = self.QUESTION_COUNT

        response = self.client.get(
            f"/bookmark/user/me/?sorted_by=added&page=2",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data["questions"])
        self.assertEqual(
            len(data["questions"]), 1 + self.QUESTION_COUNT - self.BOOKMARK_PER_PAGE
        )
        questions = data["questions"]

        for question in questions:
            self.assert_equal_question(question, vote, view_count)
            view_count += 1
            vote -= 1
