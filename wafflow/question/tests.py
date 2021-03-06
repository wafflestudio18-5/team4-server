from django.contrib.auth.models import User
from django.db import transaction
from django.test import TestCase, Client
from rest_framework.authtoken.models import Token
from rest_framework import status

from answer.models import Answer, UserAnswer
from comment.models import Comment
from question.models import Question, UserQuestion, Tag, QuestionTag
from user.models import UserProfile

import json


class QuestionTestSetting(TestCase):
    def set_up_users(self):
        self.kyh1 = User.objects.create(
            username="kyh1",
            email="kyh1@wafflow.com",
            password="password",
        )
        kyh1_profile = UserProfile.objects.create(
            user=self.kyh1,
            nickname="yh1",
            title="hi1",
            intro="Ask anything1",
        )
        Token.objects.create(user=self.kyh1)
        self.kyh1_token = "Token " + Token.objects.get(user=self.kyh1).key

        self.kyh2 = User.objects.create(
            username="kyh2",
            email="kyh2@wafflow.com",
            password="password",
        )
        kyh2_profile = UserProfile.objects.create(
            user=self.kyh2,
            nickname="yh2",
            title="hi2",
            intro="Ask anything2",
        )
        Token.objects.create(user=self.kyh2)
        self.kyh2_token = "Token " + Token.objects.get(user=self.kyh2).key

        self.kyh3 = User.objects.create(
            username="kyh3",
            email="kyh3@wafflow.com",
            password="password",
        )
        kyh3_profile = UserProfile.objects.create(
            user=self.kyh3,
            nickname="yh3",
            title="hi3",
            intro="Ask anything3",
        )
        Token.objects.create(user=self.kyh3)
        self.kyh3_token = "Token " + Token.objects.get(user=self.kyh3).key

    def set_up_questions(self):
        question1 = Question.objects.create(
            user=self.kyh1,
            title="hello1",
            content="I don't know1",
        )
        tags = "github+python+django"
        for tag in tags.split("+"):
            tag, created = Tag.objects.get_or_create(name=tag)
            QuestionTag.objects.create(question=question1, tag=tag)

        question2 = Question.objects.create(
            user=self.kyh2,
            title="hello2",
            content="I don't know2",
        )
        tags = "github+javascript+react"
        for tag in tags.split("+"):
            tag, created = Tag.objects.get_or_create(name=tag)
            QuestionTag.objects.create(question=question2, tag=tag)

        question3 = Question.objects.create(
            user=self.kyh2,
            title="hello3",
            content="I don't know3",
        )

    def check_db_count(self, **kwargs):
        user_count = kwargs.get("user_count", 3)
        user_profile_count = kwargs.get("user_profile_count", 3)
        question_count = kwargs.get("question_count", 3)
        tag_count = kwargs.get("tag_count", 5)
        question_tag_count = kwargs.get("question_tag_count", 6)
        answer_count = kwargs.get("answer_count", 0)
        comment_count = kwargs.get("comment_count", 0)
        user_question_count = kwargs.get("user_question_count", 0)
        user_answer_count = kwargs.get("user_answer_count", 0)

        self.assertEqual(User.objects.all().count(), user_count)
        self.assertEqual(UserProfile.objects.all().count(), user_profile_count)
        self.assertEqual(Question.objects.all().count(), question_count)
        self.assertEqual(Tag.objects.all().count(), tag_count)
        self.assertEqual(QuestionTag.objects.all().count(), question_tag_count)
        self.assertEqual(Answer.objects.all().count(), answer_count)
        self.assertEqual(Comment.objects.all().count(), comment_count)
        self.assertEqual(UserQuestion.objects.all().count(), user_question_count)
        self.assertEqual(UserAnswer.objects.all().count(), user_answer_count)


class QuestionInfoTestCase(QuestionTestSetting):
    def assert_in_question_info(self, data):
        author = data["author"]
        self.assertIn("id", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIn("title", data)
        self.assertIn("content", data)
        self.assertIn("vote", data)
        self.assertIn("rating", data)
        self.assertIn("has_accepted", data)
        self.assertIsNotNone(data.get("author"))
        self.assertIn("id", author)
        self.assertIn("nickname", author)
        self.assertIn("reputation", author)


class GetQuestionQuestionIdTestCase(QuestionInfoTestCase):
    client = Client()

    def setUp(self):
        self.set_up_users()
        self.set_up_questions()

    def test_get_question_question_id(self):
        question = Question.objects.get(title="hello1")

        response = self.client.get(f"/api/question/{question.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        author = data["author"]
        self.assert_in_question_info(data)
        self.assertEqual(data["content"], "I don't know1")
        self.assertEqual(data["vote"], 0)
        self.assertEqual(data["has_accepted"], False)
        self.assertEqual(author["nickname"], "yh1")
        self.assertEqual(author["reputation"], 0)
        self.assertEqual(data["comment_count"], 0)

        self.check_db_count()

    def test_get_question_wrong_question_id_(self):
        response = self.client.get(f"/api/question/-1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(f"/api/question/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

    def test_get_question_question_id_deleted_question(self):
        question = Question.objects.get(title="hello1")
        question.is_active = False
        question.save()

        response = self.client.get(f"/api/question/{question.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

    def test_get_question_question_id_comment(self):
        question = Question.objects.get(title="hello2")
        user = User.objects.get(username="kyh1")
        COMMENT_COUNT = 3

        for loop_count in range(COMMENT_COUNT):
            comment = Comment.objects.create(
                user=user,
                type=Comment.QUESTION,
                question=question,
                content="b" * (loop_count + 1),
            )

        response = self.client.get(f"/api/question/{question.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        author = data["author"]
        self.assert_in_question_info(data)
        self.assertEqual(data["content"], "I don't know2")
        self.assertEqual(data["vote"], 0)
        self.assertEqual(data["has_accepted"], False)
        self.assertEqual(author["nickname"], "yh2")
        self.assertEqual(author["reputation"], 0)
        self.assertEqual(data["comment_count"], 3)

        comment.is_active = False
        comment.save()

        response = self.client.get(f"/api/question/{question.id}/")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["comment_count"], 2)
        self.check_db_count(comment_count=3)

    def test_get_question_question_id_rating(self):
        question2 = Question.objects.get(title="hello2")
        user1 = User.objects.get(username="kyh1")
        user2 = User.objects.get(username="kyh2")
        user3 = User.objects.get(username="kyh3")

        UserQuestion.objects.create(rating=1, question=question2, user=user1)
        UserQuestion.objects.create(rating=1, question=question2, user=user3)
        question2.vote = 2
        question2.save()

        """Anonymous user의 경우"""
        response = self.client.get(f"/api/question/{question2.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        author = data["author"]
        self.assert_in_question_info(data)
        self.assertEqual(data["content"], "I don't know2")
        self.assertEqual(data["vote"], 2)
        self.assertEqual(data["has_accepted"], False)
        self.assertEqual(data["rating"], 0)
        self.assertEqual(data["view_count"], 1)
        self.assertEqual(author["nickname"], "yh2")
        self.assertEqual(Question.objects.all().count(), 3)
        self.assertEqual(UserQuestion.objects.all().count(), 2)
        self.check_db_count(user_question_count=2)

        """user의 경우"""
        response = self.client.get(
            f"/api/question/{question2.id}/", HTTP_AUTHORIZATION=self.kyh1_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        author = data["author"]
        self.assert_in_question_info(data)
        self.assertEqual(data["content"], "I don't know2")
        self.assertEqual(data["vote"], 2)
        self.assertEqual(data["has_accepted"], False)
        self.assertEqual(data["rating"], 1)
        self.assertEqual(data["view_count"], 2)
        self.assertEqual(author["nickname"], "yh2")
        self.assertEqual(Question.objects.all().count(), 3)
        self.assertEqual(UserQuestion.objects.all().count(), 2)
        self.check_db_count(user_question_count=2)


class GetQuestionUserUserIDTestCase(QuestionInfoTestCase):
    client = Client()

    def setUp(self):
        self.set_up_users()
        self.set_up_questions()

    def test_get_question_user_invalid_user_id(self):
        response = self.client.get(f"/api/question/user/-1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_question_user_user_id_sorted_by_views(self):
        user2 = User.objects.get(username="kyh2")
        response = self.client.get(
            f"/api/question/user/{user2.id}/?sorted_by=views&page=1"
        )

        data = response.json()
        if data.get("questions"):
            for question in data["questions"]:
                self.assert_in_question_info(question)
                self.assertEqual(question["view_count"], 0)
                viewed_question = Question.objects.get(id=question["id"])
                viewed_question.view_count = question["id"]
                viewed_question.save()

            response = self.client.get(
                f"/api/question/user/{user2.id}/?sorted_by=views&page=1"
            )
            data = response.json()
            self.assertIsNotNone(data.get("questions"))
            self.assertGreater(
                data["questions"][0]["view_count"], data["questions"][1]["view_count"]
            )

    def test_get_question_user_user_id_sorted_by_votes(self):
        user2 = User.objects.get(username="kyh2")
        response = self.client.get(
            f"/api/question/user/{user2.id}/?sorted_by=votes&page=1"
        )
        data = response.json()
        if data.get("questions"):
            self.assertEqual(data["questions"][0]["vote"], data["questions"][1]["vote"])
            question1 = data["questions"][0]

            for question in data["questions"]:
                self.assert_in_question_info(question)
                self.assertEqual(question["vote"], 0)
                question_change_vote = Question.objects.get(id=question["id"])
                question_change_vote.vote = question["id"]
                question_change_vote.save()

            response = self.client.get(
                f"/api/question/user/{user2.id}/?sorted_by=votes&page=1"
            )
            data = response.json()
            self.assertIsNotNone(data.get("questions"))
            self.assertGreater(
                data["questions"][0]["vote"], data["questions"][1]["vote"]
            )
            self.assertNotEqual(question1["id"], data["questions"][0]["id"])

    def test_get_question_user_user_id_sorted_by_activity(self):
        user2 = User.objects.get(username="kyh2")
        response = self.client.get(
            f"/api/question/user/{user2.id}/?sorted_by=activity&page=1"
        )
        data = response.json()
        if data.get("questions"):
            question1 = data["questions"][0]
            question2 = data["questions"][1]
            self.assertGreater(question1["updated_at"], question2["updated_at"])

            for question in data["questions"]:
                self.assert_in_question_info(question)

            question_change_acivity = Question.objects.get(id=question2["id"])
            question_change_acivity.vote = 333
            question_change_acivity.save()

            response = self.client.get(
                f"/api/question/user/{user2.id}/?sorted_by=activity&page=1"
            )
            data = response.json()
            self.assertIsNotNone(data.get("questions"))
            self.assertEqual(question1["id"], data["questions"][1]["id"])
            self.assertEqual(question2["id"], data["questions"][0]["id"])
            self.assertNotEqual(question2["vote"], data["questions"][0]["vote"])
            self.assertGreater(
                data["questions"][0]["updated_at"], data["questions"][1]["updated_at"]
            )

    def test_get_question_user_user_id_sorted_by_newest(self):
        user2 = User.objects.get(username="kyh2")
        response = self.client.get(
            f"/api/question/user/{user2.id}/?sorted_by=newest&page=1"
        )
        data = response.json()
        if data.get("questions"):
            for question in data["questions"]:
                self.assert_in_question_info(question)
            self.assertGreater(
                data["questions"][0]["created_at"], data["questions"][1]["created_at"]
            )


class GetQuestionTagsCase(QuestionInfoTestCase):
    client = Client()

    def setUp(self):
        self.set_up_users()
        self.set_up_questions()

    def test_get_question_tags_invalid_request(self):
        tags = "github"
        response = self.client.get(
            f"/api/question/tagged/?tags={tags}/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.get(
            f"/api/question/tagged/?tags={tags}&sorted_by=&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.get(
            f"/api/question/tagged/?tags={tags}&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.get(
            f"/api/question/tagged/?tags={tags}&sorted_by=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.get(
            f"/api/question/tagged/?tags={tags}&sorted_by=votes&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.get(
            f"/api/question/tagged/?tags={tags}&sorted_by=most_votes&page=asdf",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.get(
            f"/api/question/tagged/?tags={tags}&sorted_by=most_votes&page=-1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

    def test_get_question_tags_sorted_by_most_frequent(self):
        response = self.client.get(
            f"/api/question/tagged/?tags=&sorted_by=most_frequent&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()
        data = response.json()
        if data.get("questions"):
            for question in data["questions"]:
                self.assert_in_question_info(question)
                self.assertEqual(question["view_count"], 0)

                for question in data["questions"]:
                    self.assert_in_question_info(question)
                    self.assertEqual(question["view_count"], 0)
                    viewed_question = Question.objects.get(id=question["id"])
                    viewed_question.view_count = question["id"]
                    viewed_question.save()

            response = self.client.get(
                f"/api/question/tagged/?tags=&sorted_by=most_frequent&page=1",
                content_type="application/json",
            )
            data = response.json()
            self.assertIsNotNone(data.get("questions"))
            self.assertGreater(
                data["questions"][0]["view_count"], data["questions"][1]["view_count"]
            )

    def test_get_question_tags_sorted_by_most_votes(self):
        response = self.client.get(
            f"/api/question/tagged/?tags=&sorted_by=most_votes&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()
        data = response.json()
        if data.get("questions"):
            self.assertEqual(data["questions"][0]["vote"], data["questions"][1]["vote"])
            question1 = data["questions"][0]

            for question in data["questions"]:
                self.assert_in_question_info(question)
                self.assertEqual(question["vote"], 0)
                question_change_vote = Question.objects.get(id=question["id"])
                question_change_vote.vote = question["id"]
                question_change_vote.save()

            response = self.client.get(
                f"/api/question/tagged/?tags=&sorted_by=most_votes&page=1",
                content_type="application/json",
            )
            data = response.json()
            self.assertIsNotNone(data.get("questions"))
            self.assertGreater(
                data["questions"][0]["vote"], data["questions"][1]["vote"]
            )
            self.assertNotEqual(question1["id"], data["questions"][0]["id"])

    def test_get_question_tags_sorted_by_newest(self):
        response = self.client.get(
            f"/api/question/tagged/?tags=&sorted_by=newest&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()
        data = response.json()
        if data.get("questions"):
            questions = data["questions"]
            question1 = questions[0]
            question3 = questions[2]
            self.assertGreater(question1["created_at"], question3["created_at"])
            self.assertGreater(question1["id"], question3["id"])

    def test_get_question_tags_sorted_by_recent_activity(self):
        response = self.client.get(
            f"/api/question/tagged/?tags=&sorted_by=recent_activity&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()
        data = response.json()
        if data.get("questions"):
            question1 = data["questions"][0]
            question2 = data["questions"][1]
            self.assertGreater(question1["updated_at"], question2["updated_at"])

            for question in data["questions"]:
                self.assert_in_question_info(question)

            question_change_acivity = Question.objects.get(id=question2["id"])
            question_change_acivity.vote = 333
            question_change_acivity.save()

            response = self.client.get(
                f"/api/question/tagged/?tags=&sorted_by=recent_activity&page=1",
            )
            data = response.json()
            self.assertIsNotNone(data.get("questions"))
            self.assertEqual(question1["id"], data["questions"][1]["id"])
            self.assertEqual(question2["id"], data["questions"][0]["id"])
            self.assertNotEqual(question2["vote"], data["questions"][0]["vote"])
            self.assertGreater(
                data["questions"][0]["updated_at"], data["questions"][1]["updated_at"]
            )

    def test_get_question_tags_filter_by_none(self):
        response = self.client.get(
            f"/api/question/tagged/?tags=&sorted_by=newest&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()

    def test_get_question_tags_filter_by_no_answer(self):
        response = self.client.get(
            f"/api/question/tagged/?tags=&sorted_by=newest&filter_by=no_answer&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()
        data = response.json()
        answer_count = 0
        if data.get("questions"):
            self.assertEqual(len(data["questions"]), 3 - answer_count)
            question = Question.objects.get(id=data["questions"][0]["id"])
            Answer.objects.create(
                content="I know",
                question=question,
                user=self.kyh1,
            )
            answer_count += 1

        response = self.client.get(
            f"/api/question/tagged/?tags=&sorted_by=newest&filter_by=no_answer&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        if data.get("questions"):
            self.assertEqual(len(data["questions"]), 3 - answer_count)

    def test_get_question_tags_filter_by_no_accepted_answer(self):
        tags = "github+react+typescript"
        response = self.client.get(
            f"/api/question/tagged/?tags={tags}&sorted_by=newest&filter_by=no_accepted_answer&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()
        data = response.json()

        if data.get("questions"):
            self.assertEqual(len(data["questions"]), 2)
            question = Question.objects.get(id=data["questions"][0]["id"])
            with transaction.atomic():
                Answer.objects.create(
                    content="I know",
                    question=question,
                    user=self.kyh1,
                )
                answer = Answer.objects.get(user=self.kyh1)
                answer.is_accepted = True
                answer.save()
                question = Question.objects.get(id=answer.question_id)
                question.has_accepted = True
                question.save()
            response = self.client.get(
                f"/api/question/tagged/?tags={tags}&sorted_by=newest&filter_by=no_accepted_answer&page=1",
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            if data.get("questions"):
                self.assertEqual(len(data["questions"]), 1)


class GetQuestionSearchKeywordsCase(QuestionInfoTestCase):
    client = Client()

    def setUp(self):
        self.set_up_users()
        self.set_up_questions()

    def test_get_question_keywords_invalid_request(self):
        keywords = "know"
        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}&sorted_by=&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}&sorted_by=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}&sorted_by=votes&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}&sorted_by=most_votes&page=asdf",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}&sorted_by=most_votes&page=-1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

    def test_get_question_keywords_sorted_by_most_frequent(self):
        keywords = "know+spark"
        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}&tags=&sorted_by=most_frequent&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()
        data = response.json()
        if data.get("questions"):
            for question in data["questions"]:
                self.assert_in_question_info(question)
                self.assertEqual(question["view_count"], 0)

                for question in data["questions"]:
                    self.assert_in_question_info(question)
                    self.assertEqual(question["view_count"], 0)
                    viewed_question = Question.objects.get(id=question["id"])
                    viewed_question.view_count = question["id"]
                    viewed_question.save()

            response = self.client.get(
                f"/api/question/search/keywords/?keywords={keywords}&sorted_by=most_frequent&page=1",
                content_type="application/json",
            )
            data = response.json()
            self.assertIsNotNone(data.get("questions"))
            self.assertGreater(
                data["questions"][0]["view_count"], data["questions"][1]["view_count"]
            )

    def test_get_question_keywords_sorted_by_most_votes(self):
        keywords = "know+spark"
        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}&tags=&sorted_by=most_frequent&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()
        data = response.json()
        if data.get("questions"):
            self.assertEqual(data["questions"][0]["vote"], data["questions"][1]["vote"])
            question1 = data["questions"][0]

            for question in data["questions"]:
                self.assert_in_question_info(question)
                self.assertEqual(question["vote"], 0)
                question_change_vote = Question.objects.get(id=question["id"])
                question_change_vote.vote = question["id"]
                question_change_vote.save()

            response = self.client.get(
                f"/api/question/search/keywords/?keywords={keywords}&tags=&sorted_by=most_frequent&page=1",
                content_type="application/json",
            )
            data = response.json()
            self.assertIsNotNone(data.get("questions"))
            self.assertGreater(
                data["questions"][0]["vote"], data["questions"][1]["vote"]
            )
            self.assertNotEqual(question1["id"], data["questions"][0]["id"])

    def test_get_question_keywords_sorted_by_newest(self):
        keywords = "know+spark"
        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}&tags=&sorted_by=most_frequent&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()
        data = response.json()
        if data.get("questions"):
            questions = data["questions"]
            question1 = questions[0]
            question3 = questions[2]
            self.assertGreater(question1["created_at"], question3["created_at"])
            self.assertGreater(question1["id"], question3["id"])

    def test_get_question_keywords_sorted_by_recent_activity(self):
        keywords = "know+spark"
        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}&tags=&sorted_by=most_frequent&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()
        data = response.json()
        if data.get("questions"):
            question1 = data["questions"][0]
            question2 = data["questions"][1]
            self.assertGreater(question1["updated_at"], question2["updated_at"])

            for question in data["questions"]:
                self.assert_in_question_info(question)

            question_change_acivity = Question.objects.get(id=question2["id"])
            question_change_acivity.vote = 333
            question_change_acivity.save()

            response = self.client.get(
                f"/api/question/search/keywords/?keywords={keywords}&tags=&sorted_by=most_frequent&page=1",
                content_type="application/json",
            )
            data = response.json()
            self.assertIsNotNone(data.get("questions"))
            self.assertEqual(question1["id"], data["questions"][1]["id"])
            self.assertEqual(question2["id"], data["questions"][0]["id"])
            self.assertNotEqual(question2["vote"], data["questions"][0]["vote"])
            self.assertGreater(
                data["questions"][0]["updated_at"], data["questions"][1]["updated_at"]
            )

    def test_get_question_keywords_filter_by_none(self):
        keywords = "know+spark"
        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}&tags=&sorted_by=most_frequent&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()

    def test_get_question_keywords_filter_by_no_answer(self):
        keywords = "know+spark"
        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}&tags=&sorted_by=most_frequent&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()
        data = response.json()
        answer_count = 0
        if data.get("questions"):
            self.assertEqual(len(data["questions"]), 3 - answer_count)
            question = Question.objects.get(id=data["questions"][0]["id"])
            Answer.objects.create(
                content="I know",
                question=question,
                user=self.kyh1,
            )
            answer_count += 1

            response = self.client.get(
                f"/api/question/search/keywords/?keywords={keywords}&tags=&sorted_by=most_frequent&page=1",
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            if data.get("questions"):
                self.assertEqual(len(data["questions"]), 3 - answer_count)

    def test_get_question_keywords_filter_by_no_accepted_answer(self):
        keywords = "know+spark"
        response = self.client.get(
            f"/api/question/search/keywords/?keywords={keywords}&tags=&sorted_by=most_frequent&page=1",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_db_count()
        data = response.json()

        if data.get("questions"):
            self.assertEqual(len(data["questions"]), 2)
            question = Question.objects.get(id=data["questions"][0]["id"])
            with transaction.atomic():
                Answer.objects.create(
                    content="I know",
                    question=question,
                    user=self.kyh1,
                )
                answer = Answer.objects.get(user=self.kyh1)
                answer.is_accepted = True
                answer.save()
                question = Question.objects.get(id=answer.question_id)
                question.has_accepted = True
                question.save()
            response = self.client.get(
                f"/api/question/search/keywords/?keywords={keywords}&tags=&sorted_by=most_frequent&page=1",
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            if data.get("questions"):
                self.assertEqual(len(data["questions"]), 1)


class PostQuestionTestCase(QuestionInfoTestCase):
    client = Client()

    def setUp(self):
        self.set_up_users()
        self.set_up_questions()

    def test_post_question_invalid_token(self):
        response = self.client.post(
            f"/api/question/",
            json.dumps({"title": "hello4", "content": "I don't know4"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.check_db_count()

        response = self.client.post(
            f"/api/question/",
            json.dumps({"title": "hello4", "content": "I don't know4"}),
            HTTP_AUTHORIZATION="asdf",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.check_db_count()

    def test_post_question_invalid_request(self):
        response = self.client.post(
            f"/api/question/",
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.post(
            f"/api/question/",
            json.dumps({"title": "hello4"}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.post(
            f"/api/question/",
            json.dumps({"content": "I don't know4"}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.post(
            f"/api/question/",
            json.dumps({"title": ""}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.post(
            f"/api/question/",
            json.dumps({"content": ""}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

    def test_post_question_too_long_title(self):
        response = self.client.post(
            f"/api/question/",
            json.dumps({"title": "h" * 201, "content": "a"}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

    def test_post_question_too_long_content(self):
        response = self.client.post(
            f"/api/question/",
            json.dumps({"title": "hello4", "content": "a" * 5001}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

    def test_post_question(self):
        response = self.client.post(
            f"/api/question/",
            json.dumps(
                {
                    "title": "hello4",
                    "content": "I don't know4",
                    "tags": ["C++", "python"],
                }
            ),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assert_in_question_info(data)
        self.assertEqual(data["title"], "hello4")
        self.assertEqual(data["content"], "I don't know4")
        self.assertEqual(len(data["tags"]), 2)
        self.check_db_count(question_count=4, tag_count=6, question_tag_count=8)


class PutQuestionTestCase(QuestionInfoTestCase):
    client = Client()

    def setUp(self):
        self.set_up_users()
        self.set_up_questions()

    def test_put_question_invalid_request(self):
        response = self.client.put(
            f"/api/question/-1/",
            json.dumps({"title": "hello4", "content": "I don't know4"}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

        question_last = Question.objects.all().last()
        response = self.client.put(
            f"/api/question/{question_last.id + 1}/",
            json.dumps({"title": "hello4", "content": "I don't know4"}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

        user_question_last = self.kyh1.questions.last()
        response = self.client.put(
            f"/api/question/{user_question_last.id}/",
            json.dumps({"title": "hello4", "content": "I don't know4"}),
            HTTP_AUTHORIZATION=self.kyh2_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.check_db_count()

        response = self.client.put(
            f"/api/question/{user_question_last.id}/",
            json.dumps({"title": "hello4", "content": "I don't know4"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.check_db_count()

        response = self.client.put(
            f"/api/question/{user_question_last.id}/",
            json.dumps({"title": "a" * 201, "content": "I don't know4"}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

        response = self.client.put(
            f"/api/question/{user_question_last.id}/",
            json.dumps({"title": "hello4", "content": "a" * 5001}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

    def test_put_question(self):
        user_question_last = self.kyh1.questions.last()
        response = self.client.put(
            f"/api/question/{user_question_last.id}/",
            json.dumps({"title": "hello444", "content": "I don't know44"}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            [data["title"], data["content"]], ["hello444", "I don't know44"]
        )
        self.check_db_count()

        response = self.client.put(
            f"/api/question/{user_question_last.id}/",
            json.dumps({"title": "", "content": "I don't know4"}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            [data["title"], data["content"]], ["hello444", "I don't know4"]
        )
        self.check_db_count()

        response = self.client.put(
            f"/api/question/{user_question_last.id}/",
            json.dumps({"title": "hello4", "content": ""}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            [data["title"], data["content"]], ["hello4", "I don't know4"]
        )
        self.check_db_count()

        response = self.client.put(
            f"/api/question/{user_question_last.id}/",
            json.dumps({"title": "hello4"}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            [data["title"], data["content"]], ["hello4", "I don't know4"]
        )
        self.check_db_count()

        response = self.client.put(
            f"/api/question/{user_question_last.id}/",
            json.dumps({"content": "I don't know4"}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            [data["title"], data["content"]], ["hello4", "I don't know4"]
        )
        self.check_db_count()

        response = self.client.put(
            f"/api/question/{user_question_last.id}/",
            json.dumps({}),
            HTTP_AUTHORIZATION=self.kyh1_token,
            content_type="application/json",
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            [data["title"], data["content"]], ["hello4", "I don't know4"]
        )
        self.check_db_count()
