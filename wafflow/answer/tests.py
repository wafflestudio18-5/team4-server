from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.authtoken.models import Token

from answer.models import Answer, UserAnswer
from comment.models import Comment
from question.models import Question
from user.models import UserProfile

import json


class UserQuestionTestSetting(TestCase):
    def set_up_user_question(self):
        eldpswp99 = User.objects.create_user(
            username="eldpswp99", email="nrg1392@naver.com", password="password"
        )
        eldpswp99_profile = UserProfile.objects.create(
            user=eldpswp99,
            nickname="MyungHoon Park",
            intro="Hello World!",
        )
        Token.objects.create(user=eldpswp99)
        self.eldpswp99_token = "Token " + Token.objects.get(user=eldpswp99).key
        qwerty = User.objects.create_user(
            username="qwerty", email="nrg1392@naver.com", password="password"
        )
        qwerty_profile = UserProfile.objects.create(
            user=qwerty, nickname="example", intro="1q2w3e4r", reputation=1234
        )
        Token.objects.create(user=qwerty)
        question = Question.objects.create(
            user=eldpswp99,
            title="Hello",
            content="World",
        )
        self.qwerty_token = "Token " + Token.objects.get(user=qwerty).key

    def check_db_count(self, **kwargs):
        answer_count = kwargs.get("answer_count", 0)
        question_count = kwargs.get("question_count", 1)
        user_count = kwargs.get("user_count", 2)
        user_profile_count = kwargs.get("user_profile_count", 2)
        comment_count = kwargs.get("comment_count", 0)
        user_answer_count = kwargs.get("user_answer_count", 0)

        self.assertEqual(Answer.objects.all().count(), answer_count)
        self.assertEqual(Question.objects.all().count(), question_count)
        self.assertEqual(User.objects.all().count(), user_count)
        self.assertEqual(UserProfile.objects.all().count(), user_profile_count)
        self.assertEqual(Comment.objects.all().count(), comment_count)
        self.assertEqual(UserAnswer.objects.all().count(), user_answer_count)


class GetAnswerInfoTestCase(UserQuestionTestSetting):
    def assert_in_answer_info(self, data):
        self.assertIn("id", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIn("content", data)
        self.assertIn("vote", data)
        self.assertIn("is_accepted", data)
        self.assertIn("rating", data)
        self.assertIsNotNone(data["author"])

        author = data["author"]
        self.assertIn("id", author)
        self.assertIn("username", author)
        self.assertIn("reputation", author)


class MultipleAnswerSetUp(UserQuestionTestSetting):
    def setUp(self):
        self.set_up_user_question()
        eldpswp99 = User.objects.get(username="eldpswp99")

        question = Question.objects.get(title="Hello")

        self.WHOLE_ANSWER_COUNT = 46
        self.ANSWER_COUNT = 45
        self.ANSWER_PER_PAGE = 30
        for loop_count in range(self.ANSWER_COUNT):
            Answer.objects.create(
                content=str(loop_count + 1),
                question=question,
                user=eldpswp99,
                vote=loop_count + 1,
            )

        Answer.objects.create(
            content=str(1),
            question=question,
            user=eldpswp99,
            vote=self.ANSWER_COUNT + 1,
            is_active=False,
        )

    def check_db_count(self, **kwargs):
        answer_count = kwargs.get("answer_count", self.WHOLE_ANSWER_COUNT)
        question_count = kwargs.get("question_count", 1)
        user_count = kwargs.get("user_count", 2)
        user_profile_count = kwargs.get("user_profile_count", 2)
        comment_count = kwargs.get("comment_count", 0)
        user_answer_count = kwargs.get("user_answer_count", 0)

        super().check_db_count(
            answer_count=answer_count,
            question_count=question_count,
            user_count=user_count,
            user_profile_count=user_profile_count,
            comment_count=comment_count,
            user_answer_count=user_answer_count,
        )


class GetAnswerAnswerIdTestCase(GetAnswerInfoTestCase):
    client = Client()
    ANSWER_COUNT = 3

    def check_db_count(self, **kwargs):
        answer_count = kwargs.get("answer_count", 6)
        question_count = kwargs.get("question_count", 1)
        user_count = kwargs.get("user_count", 2)
        user_profile_count = kwargs.get("user_profile_count", 2)
        comment_count = kwargs.get("comment_count", 1)
        user_answer_count = kwargs.get("user_answer_count", 0)

        super().check_db_count(
            answer_count=answer_count,
            question_count=question_count,
            user_count=user_count,
            user_profile_count=user_profile_count,
            comment_count=comment_count,
            user_answer_count=user_answer_count,
        )

    def setUp(self):
        self.set_up_user_question()
        eldpswp99 = User.objects.get(username="eldpswp99")
        qwerty = User.objects.get(username="qwerty")

        question = Question.objects.get(title="Hello")
        for loop_count in range(self.ANSWER_COUNT):
            Answer.objects.create(
                user=eldpswp99, question=question, content=str(loop_count + 1)
            )
        for loop_count in range(self.ANSWER_COUNT):
            Answer.objects.create(
                user=qwerty, question=question, content="b" * (loop_count + 1)
            )

        comment = Comment.objects.create(
            user=eldpswp99,
            type=Comment.ANSWER,
            answer=Answer.objects.get(content="1"),
            content="content",
        )

    def test_get_answer_answer_id(self):
        answer = Answer.objects.get(content="1")
        answer.is_accepted = True
        answer.save()

        response = self.client.get(f"/answer/{answer.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assert_in_answer_info(data)
        self.assertEqual(data["content"], "1")
        self.assertEqual(data["vote"], 0)
        self.assertEqual(data["is_accepted"], True)
        self.assertEqual(data["rating"], 0)

        author = data["author"]
        self.assertEqual(author["username"], "eldpswp99")
        self.assertEqual(author["reputation"], 0)

        self.assertEqual(data["comment_count"], 1)

        self.check_db_count()

    def test_get_answer_answer_id_wrong_request(self):
        response = self.client.get(f"/answer/-1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(f"/answer/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

    def test_get_answer_answer_id_deleted_answer(self):
        answer = Answer.objects.get(content="1")
        answer.is_active = False
        answer.save()

        response = self.client.get(f"/answer/{answer.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

    def test_get_answer_answer_id_deleted_comment(self):
        answer = Answer.objects.get(content="b")
        user = User.objects.get(username="qwerty")
        COMMENT_COUNT = 3

        for loop_count in range(COMMENT_COUNT):
            comment = Comment.objects.create(
                user=user,
                type=Comment.ANSWER,
                answer=answer,
                content="b" * (loop_count + 1),
            )

        response = self.client.get(f"/answer/{answer.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assert_in_answer_info(data)
        self.assertEqual(data["content"], "b")
        self.assertEqual(data["vote"], 0)
        self.assertEqual(data["is_accepted"], False)
        self.assertEqual(data["rating"], 0)

        author = data["author"]
        self.assertEqual(author["username"], "qwerty")
        self.assertEqual(author["reputation"], 1234)
        self.assertEqual(data["comment_count"], 3)

        comment.is_active = False
        comment.save()

        response = self.client.get(f"/answer/{answer.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["comment_count"], 2)

        self.check_db_count(comment_count=4)

    def test_get_answer_answer_id_with_rating(self):
        answer = Answer.objects.get(content="1")
        eldpswp99 = User.objects.get(username="eldpswp99")
        qwerty = User.objects.get(username="qwerty")
        user_answer = UserAnswer.objects.create(rating=1, answer=answer, user=eldpswp99)
        user_answer = UserAnswer.objects.create(rating=1, answer=answer, user=qwerty)

        answer.vote = 2
        answer.save()

        response = self.client.get(
            f"/answer/{answer.id}/", HTTP_AUTHORIZATION=self.eldpswp99_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assert_in_answer_info(data)
        self.assertEqual(data["content"], "1")
        self.assertEqual(data["vote"], 2)
        self.assertEqual(data["is_accepted"], False)
        self.assertEqual(data["rating"], 1)

        author = data["author"]
        self.assertEqual(author["username"], "eldpswp99")
        self.assertEqual(author["reputation"], 0)
        self.assertEqual(data["comment_count"], 1)

        self.assertEqual(Answer.objects.all().count(), 6)
        self.assertEqual(Question.objects.all().count(), 1)
        self.assertEqual(User.objects.all().count(), 2)
        self.assertEqual(UserProfile.objects.all().count(), 2)
        self.assertEqual(Comment.objects.all().count(), 1)
        self.assertEqual(UserAnswer.objects.all().count(), 2)
        self.check_db_count(user_answer_count=2)


class GetAnswerUserUserIDTestCase(MultipleAnswerSetUp):
    client = Client()

    def assert_in_answer_info(self, data):
        self.assertIn("id", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data),
        self.assertIn("title", data),
        self.assertIn("vote", data),
        self.assertIn("is_accepted", data)

    def test_get_answer_user_user_id_invalid_id(self):
        response = self.client.get(f"/answer/user/-1/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

    def test_get_answer_user_user_id_invalid_sorted_by(self):
        user = User.objects.get(username="eldpswp99")
        response = self.client.get(f"/answer/user/{user.id}/?sorted_by=asdf&page={1}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

    def test_get_answer_user_user_id_deleted_user(self):
        user = User.objects.get(username="eldpswp99")
        user.is_active = False
        user.save()
        response = self.client.get(f"/answer/user/{user.id}/?sorted_by=votes&page={1}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

    def test_get_answer_user_user_id_invalid_page(self):
        user = User.objects.get(username="eldpswp99")
        response = self.client.get(f"/answer/user/{user.id}/?sorted_by=votes&page=-1")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            f"/answer/user/{user.id}/?sorted_by=votes&page=99999"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

    def test_get_answer_user_user_id_sorted_by_votes(self):
        user = User.objects.get(username="eldpswp99")

        ACCEPTED_ANSWER_VOTE = 34
        answer = Answer.objects.get(vote=ACCEPTED_ANSWER_VOTE)
        answer.is_accepted = True
        answer.save()

        response = self.client.get(f"/answer/user/{user.id}/?sorted_by=votes&page=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIsNotNone(data["answers"])

        answers = data["answers"]

        self.assertEqual(len(answers), self.ANSWER_PER_PAGE)
        vote = self.ANSWER_COUNT
        for answer in answers:
            self.assert_in_answer_info(answer)
            self.assertEqual(answer["title"], "Hello"),
            self.assertEqual(answer["vote"], vote)
            self.assertEqual(
                answer["is_accepted"], False if vote != ACCEPTED_ANSWER_VOTE else True
            )
            vote -= 1

        response = self.client.get(f"/answer/user/{user.id}/?sorted_by=votes&page=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIsNotNone(data["answers"])
        answers = data["answers"]

        self.assertEqual(len(answers), self.ANSWER_COUNT - self.ANSWER_PER_PAGE)
        for answer in answers:
            self.assert_in_answer_info(answer)
            self.assertEqual(answer["title"], "Hello"),
            self.assertEqual(answer["vote"], vote)
            vote -= 1
            self.assertEqual(answer["is_accepted"], False)

        self.check_db_count()

    def test_get_answer_user_user_id_sorted_by_updated_at(self):
        user = User.objects.get(username="eldpswp99")
        ACCEPTED_VOTE = 11
        CHANGE_VOTE = 3

        answer_accepted = Answer.objects.get(vote=ACCEPTED_VOTE)
        answer_accepted.is_accepted = True
        answer_accepted.save()

        answer_change_vote = Answer.objects.get(vote=CHANGE_VOTE)
        answer_change_vote.vote = 100
        answer_change_vote.save()

        response = self.client.get(f"/answer/user/{user.id}/?sorted_by=activity&page=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIsNotNone(data["answers"])
        answers = data["answers"]
        self.assertEqual(len(answers), self.ANSWER_PER_PAGE)
        idx = 0
        vote = self.ANSWER_COUNT
        for answer in answers:
            self.assert_in_answer_info(answer)
            self.assertEqual(answer["title"], "Hello")
            if idx == 0:
                self.assertEqual(answer["vote"], 100)
            elif idx == 1:
                self.assertEqual(answer["vote"], ACCEPTED_VOTE)
            else:
                self.assertEqual(answer["vote"], vote)
                vote -= 1
            self.assertEqual(
                answer["is_accepted"],
                False if answer["vote"] != ACCEPTED_VOTE else True,
            )

            idx += 1

        response = self.client.get(f"/answer/user/{user.id}/?sorted_by=activity&page=2")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIsNotNone(data["answers"])
        answers = data["answers"]
        self.assertEqual(len(answers), self.ANSWER_COUNT - self.ANSWER_PER_PAGE)
        for answer in answers:
            self.assert_in_answer_info(answer)
            self.assertEqual(answer["title"], "Hello")
            self.assertEqual(answer["vote"], vote)
            self.assertEqual(answer["is_accepted"], False)
            vote -= 1
            if vote in [ACCEPTED_VOTE, CHANGE_VOTE]:
                vote -= 1

        self.check_db_count()

    def test_get_answer_user_user_id_sorted_by_newest(self):
        user = User.objects.get(username="eldpswp99")
        question = Question.objects.get(title="Hello")
        CREATE_COUNT = 3
        for answer in range(CREATE_COUNT):
            Answer.objects.create(user=user, question=question, vote=100 + answer)

        response = self.client.get(f"/answer/user/{user.id}/?sorted_by=newest&page=1")
        data = response.json()
        self.assertIsNotNone(data["answers"])
        answers = data["answers"]

        vote = 102
        for answer in answers:
            self.assert_in_answer_info(answer)
            self.assertEqual(answer["title"], "Hello")
            self.assertEqual(answer["vote"], vote)
            vote -= 1
            if vote == 99:
                vote = 45
            self.assertEqual(answer["is_accepted"], False)

        response = self.client.get(f"/answer/user/{user.id}/?sorted_by=newest&page=2")

        data = response.json()
        self.assertIsNotNone(data["answers"])
        answers = data["answers"]
        self.assertEqual(
            len(answers), self.ANSWER_COUNT - self.ANSWER_PER_PAGE + CREATE_COUNT
        )
        for answer in answers:
            self.assert_in_answer_info(answer)
            self.assertEqual(answer["title"], "Hello")
            self.assertEqual(answer["vote"], vote)
            vote -= 1
            self.assertEqual(answer["is_accepted"], False)

        self.check_db_count(answer_count=self.WHOLE_ANSWER_COUNT + CREATE_COUNT)

    def test_get_answer_user_user_id_no_answer(self):
        user = User.objects.get(username="qwerty")

        response = self.client.get(f"/answer/user/{user.id}/?sorted_by=votes&page=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIsNotNone(data["answers"])
        self.assertEqual(len(data["answers"]), 0)

        self.check_db_count()


class GetAnswerQuestionQuestionIDTestCase(GetAnswerInfoTestCase, MultipleAnswerSetUp):
    client = Client()

    def test_get_answer_question_question_id_invalid_id(self):
        response = self.client.get(f"/answer/question/{-1}/?sorted_by=votes&page=1")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

    def test_get_answer_question_question_id_deleted_question(self):
        question = Question.objects.get(title="Hello")
        question.is_active = False
        question.save()

        response = self.client.get(
            f"/answer/question/{question.id}/?sorted_by=votes&page=1"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

    def test_get_answer_question_question_id_invalid_sorted_by(self):
        question = Question.objects.get(title="Hello")

        response = self.client.get(
            f"/answer/question/{question.id}/?sorted_by=asdf&page=1"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

    def test_get_answer_question_question_id_invalid_page(self):
        question = Question.objects.get(title="Hello")

        response = self.client.get(
            f"/answer/question/{question.id}/?sorted_by=votes&page=-1"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            f"/answer/question/{question.id}/?sorted_by=votes&page=9999"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

    def test_get_answer_question_question_id_no_answer(self):
        qwerty = User.objects.get(username="qwerty")
        question = Question.objects.create(
            user=qwerty, title="django", content="server"
        )

        response = self.client.get(
            f"/answer/question/{question.id}/?sorted_by=votes&page=1"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIsNotNone(data["answers"])
        self.assertEqual(len(data["answers"]), 0)

        self.check_db_count(question_count=2)

    def test_get_answer_question_question_id_sorted_by_votes(self):
        question = Question.objects.get(title="Hello")
        qwerty = User.objects.get(username="qwerty")
        eldpswp99_profile = User.objects.get(username="eldpswp99").profile
        eldpswp99_profile.reputation = 35
        eldpswp99_profile.save()
        accepted_answer = Answer.objects.get(vote=1)
        accepted_answer.is_accepted = True
        accepted_answer.save()
        rating = UserAnswer.objects.create(
            user=qwerty, answer=accepted_answer, rating=1
        )
        for comment_count in range(3):
            comment = Comment.objects.create(
                content="good", type=Comment.ANSWER, user=qwerty, answer=accepted_answer
            )

        response = self.client.get(
            f"/answer/question/{question.id}/?sorted_by=votes&page=1",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        data = response.json()
        self.assertIsNotNone(data["answers"])
        self.assertEqual(len(data["answers"]), self.ANSWER_PER_PAGE)
        answers = data["answers"]
        vote = 1

        for answer in answers:
            if vote == 0:
                vote = 45
            self.assert_in_answer_info(answer)
            self.assertEqual(answer["content"], str(vote))
            self.assertEqual(answer["vote"], vote)
            self.assertEqual(answer["is_accepted"], True if vote == 1 else False)
            self.assertEqual(answer["rating"], 1 if vote == 1 else 0)
            self.assertEqual(answer["comment_count"], 3 if vote == 1 else 0)
            author = answer["author"]
            self.assertEqual(author["username"], "eldpswp99")
            self.assertEqual(author["reputation"], 35)
            vote -= 1

        response = self.client.get(
            f"/answer/question/{question.id}/?sorted_by=votes&page=2",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        data = response.json()
        self.assertIsNotNone(data["answers"])
        self.assertEqual(len(data["answers"]), self.ANSWER_COUNT - self.ANSWER_PER_PAGE)
        answers = data["answers"]

        for answer in answers:
            self.assert_in_answer_info(answer)
            self.assertEqual(answer["content"], str(vote))
            self.assertEqual(answer["vote"], vote)
            self.assertEqual(answer["is_accepted"], False)
            self.assertEqual(answer["rating"], 0)
            self.assertEqual(answer["comment_count"], 0)
            author = answer["author"]
            self.assertEqual(author["username"], "eldpswp99")
            self.assertEqual(author["reputation"], 35)
            vote -= 1

        self.check_db_count(user_answer_count=1, comment_count=3)

    def test_get_question_question_id_sorted_by_updated_at(self):
        question = Question.objects.get(title="Hello")
        ACCEPTED_VOTE = 11
        CHANGE_VOTE = 3

        answer_accepted = Answer.objects.get(vote=ACCEPTED_VOTE)
        answer_accepted.is_accepted = True
        answer_accepted.save()

        answer_change_vote = Answer.objects.get(vote=CHANGE_VOTE)
        answer_change_vote.vote = 100
        answer_change_vote.save()

        eldpswp99_profile = User.objects.get(username="eldpswp99").profile
        eldpswp99_profile.reputation = 123
        eldpswp99_profile.save()
        qwerty = User.objects.get(username="qwerty")
        rating = UserAnswer.objects.create(
            user=qwerty, answer=answer_accepted, rating=1
        )

        for comment in range(3):
            Comment.objects.create(
                user=qwerty, answer=answer_accepted, content="b", type=Comment.ANSWER
            )

        response = self.client.get(
            f"/answer/question/{question.id}/?sorted_by=activity&page=1",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIsNotNone(data["answers"])
        answers = data["answers"]
        self.assertEqual(len(answers), self.ANSWER_PER_PAGE)
        idx = 0
        vote = self.ANSWER_COUNT
        for answer in answers:
            self.assert_in_answer_info(answer)
            if idx == 0:
                self.assertEqual(answer["vote"], ACCEPTED_VOTE)
                self.assertEqual(answer["content"], str(ACCEPTED_VOTE))
                self.assertEqual(answer["comment_count"], 3)
                self.assertEqual(answer["rating"], 1)
            elif idx == 1:
                self.assertEqual(answer["vote"], 100)
                self.assertEqual(answer["content"], str(CHANGE_VOTE))
            else:
                self.assertEqual(answer["vote"], vote)
                self.assertEqual(answer["content"], str(vote))
                vote -= 1

            if idx != 0:
                self.assertEqual(answer["comment_count"], 0)
                self.assertEqual(answer["rating"], 0)

            author = answer["author"]
            self.assertEqual(author["username"], "eldpswp99")
            self.assertEqual(author["reputation"], 123)
            self.assertEqual(
                answer["is_accepted"],
                False if answer["vote"] != ACCEPTED_VOTE else True,
            )

            idx += 1

        response = self.client.get(
            f"/answer/question/{question.id}/?sorted_by=activity&page=2",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIsNotNone(data["answers"])
        answers = data["answers"]
        self.assertEqual(len(answers), self.ANSWER_COUNT - self.ANSWER_PER_PAGE)
        for answer in answers:
            self.assert_in_answer_info(answer)
            self.assertEqual(answer["content"], str(vote))
            self.assertEqual(answer["vote"], vote)
            self.assertEqual(answer["is_accepted"], False)
            self.assertEqual(answer["rating"], 0)
            self.assertEqual(answer["comment_count"], 0)
            author = answer["author"]
            self.assertEqual(author["username"], "eldpswp99")
            self.assertEqual(author["reputation"], 123)

            vote -= 1
            if vote in [ACCEPTED_VOTE, CHANGE_VOTE]:
                vote -= 1

        self.check_db_count(user_answer_count=1, comment_count=3)

    def test_get_question_question_question_id_sorted_by_oldest(self):
        question = Question.objects.get(title="Hello")
        qwerty = User.objects.get(username="qwerty")
        qwerty_profile = qwerty.profile
        qwerty_profile.reputation = 100
        qwerty_profile.save()

        NEW_VOTE = self.ANSWER_COUNT + 1
        ACCEPTED_VOTE = 13
        accepted_answer = Answer.objects.get(vote=ACCEPTED_VOTE)
        accepted_answer.is_accepted = True
        accepted_answer.save()

        answer = Answer.objects.create(
            user=qwerty, question=question, content=str(NEW_VOTE), vote=NEW_VOTE
        )

        Comment.objects.create(
            user=qwerty, answer=answer, content="hello", type=Comment.ANSWER
        )

        UserAnswer.objects.create(user=qwerty, answer=answer, rating=-1)

        response = self.client.get(
            f"/answer/question/{question.id}/?sorted_by=oldest&page=1",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIsNotNone(data["answers"])
        answers = data["answers"]
        self.assertEqual(len(answers), self.ANSWER_PER_PAGE)
        idx = 0
        vote = 1
        for answer in answers:
            self.assert_in_answer_info(answer)
            if idx == 0:
                self.assertEqual(answer["vote"], ACCEPTED_VOTE)
                self.assertEqual(answer["content"], str(ACCEPTED_VOTE))
            else:
                self.assertEqual(answer["vote"], vote)
                self.assertEqual(answer["content"], str(vote))
                vote += 1
                if vote == ACCEPTED_VOTE:
                    vote += 1

            author = answer["author"]
            self.assertEqual(answer["comment_count"], 0)
            self.assertEqual(author["username"], "eldpswp99")
            self.assertEqual(author["reputation"], 0)
            self.assertEqual(
                answer["is_accepted"],
                False if answer["vote"] != ACCEPTED_VOTE else True,
            )

            idx += 1

        response = self.client.get(
            f"/answer/question/{question.id}/?sorted_by=oldest&page=2",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIsNotNone(data["answers"])
        answers = data["answers"]
        self.assertEqual(len(answers), 1 + self.ANSWER_COUNT - self.ANSWER_PER_PAGE)
        for answer in answers:
            self.assert_in_answer_info(answer)
            self.assertEqual(answer["content"], str(vote))
            self.assertEqual(answer["vote"], vote)
            self.assertEqual(answer["is_accepted"], False)
            self.assertEqual(answer["rating"], 0 if vote != NEW_VOTE else -1)
            self.assertEqual(answer["comment_count"], 0 if vote != NEW_VOTE else 1)
            author = answer["author"]
            self.assertEqual(
                author["username"], "eldpswp99" if vote != NEW_VOTE else "qwerty"
            )
            self.assertEqual(author["reputation"], 0 if vote != NEW_VOTE else 100)
            vote += 1

        self.check_db_count(
            answer_count=(self.WHOLE_ANSWER_COUNT + 1),
            comment_count=1,
            user_answer_count=1,
        )


class PostPutAnswerTestCase(UserQuestionTestSetting):
    def assert_in_answer_info(self, data):
        self.assertIn("id", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIn("content", data)
        self.assertIn("vote", data)
        self.assertIn("is_accepted", data)
        self.assertIn("rating", data)
        self.assertIn("comment_count", data)


class PostAnswerTestCase(PostPutAnswerTestCase):
    client = Client()

    def check_db_count(self, **kwargs):
        answer_count = kwargs.get("answer_count", 0)

        super().check_db_count(answer_count=answer_count)

    def setUp(self):
        self.set_up_user_question()

    def test_post_answer_question_question_id_invalid_token(self):
        question = Question.objects.get(title="Hello")

        response = self.client.post(
            f"/answer/question/{question.id}/",
            json.dumps({"content": "world"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(
            f"/answer/question/{question.id}/",
            json.dumps({"content": "world"}),
            HTTP_AUTHORIZATION="asdf",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.check_db_count()

    def post_answer_question_question_id_invalid_question_id(self):
        response = self.client.post(
            f"/answer/question/-1/",
            json.dumps({"content": "world"}),
            HTTP_AUTHORIZATION=self.eldpswp99_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

    def post_answer_question_question_id_deleted_question(self):
        question = Question.objects.get(title="Hello")
        question.is_active = False
        question.save()

        response = self.client.post(
            f"/answer/question/{question.id}/",
            json.dumps({"content": "world"}),
            HTTP_AUTHORIZATION=self.eldpswp99_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_db_count()

    def post_answer_question_question_id_invalid_content(self):
        question = Question.objects.get(title="Hello")

        response = self.client.post(
            f"/answer/question/{question.id}",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            f"/answer/question/{question.id}",
            json.dumps({"content": ""}),
            HTTP_AUTHORIZATION=self.eldpswp99_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

    def test_post_answer_question_question_id_too_long_content(self):
        question = Question.objects.get(title="Hello")

        response = self.client.post(
            f"/answer/question/{question.id}/",
            json.dumps({"content": "a" * 5001}),
            HTTP_AUTHORIZATION=self.eldpswp99_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

    def test_post_answer_question_question_id(self):
        question = Question.objects.get(title="Hello")

        response = self.client.post(
            f"/answer/question/{question.id}/",
            json.dumps({"content": "world"}),
            HTTP_AUTHORIZATION=self.eldpswp99_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assert_in_answer_info(data)
        self.assertEqual(data["content"], "world")
        self.assertEqual(data["vote"], 0)
        self.assertEqual(data["is_accepted"], False)
        self.assertEqual(data["rating"], 0)
        self.assertEqual(data["comment_count"], 0)
        self.check_db_count(answer_count=1)


class PutAnswerTestCase(PostPutAnswerTestCase):
    client = Client()

    def check_db_count(self, **kwargs):
        answer_count = kwargs.get("answer_count", 1)

        super().check_db_count(answer_count=answer_count)

    def setUp(self):
        self.set_up_user_question()
        eldpswp99 = User.objects.get(username="eldpswp99")
        question = Question.objects.get(title="Hello")

        Answer.objects.create(
            user=eldpswp99, question=question, content="world", vote=2
        )

    def test_put_answer_answer_id_invalid_token(self):
        answer = Answer.objects.get(content="world")

        response = self.client.put(
            f"/answer/{answer.id}/",
            json.dumps({"content": "asdf"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(
            f"/answer/{answer.id}/",
            json.dumps({"content": "asdf"}),
            HTTP_AUTHORIZATION="asdf",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.check_db_count()

    def test_put_answer_answer_id_invalid_id(self):
        response = self.client.put(
            f"/answer/-1/",
            json.dumps({"content": "asdf"}),
            HTTP_AUTHORIZATION=self.eldpswp99_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_answer_answer_id_deleted_answer(self):
        answer = Answer.objects.get(content="world")
        answer.is_active = False
        answer.save()

        response = self.client.put(
            f"/answer/{answer.id}/",
            json.dumps({"content": "asdf"}),
            HTTP_AUTHORIZATION=self.eldpswp99_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_answer_answer_id_not_allowed_user(self):
        answer = Answer.objects.get(content="world")

        response = self.client.put(
            f"/answer/{answer.id}/",
            json.dumps({"content": "asdf"}),
            HTTP_AUTHORIZATION=self.qwerty_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.check_db_count()

    def test_put_answer_answer_id_too_long_content(self):
        answer = Answer.objects.get(content="world")

        response = self.client.put(
            f"/answer/{answer.id}/",
            json.dumps({"content": "a" * 5001}),
            HTTP_AUTHORIZATION=self.eldpswp99_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()

    def test_put_answer_answer_id_blank_or_none_content(self):
        answer = Answer.objects.get(content="world")

        response = self.client.put(
            f"/answer/{answer.id}/",
            json.dumps({}),
            HTTP_AUTHORIZATION=self.eldpswp99_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assert_in_answer_info(data)
        self.assertEqual(data["content"], "world")
        self.assertEqual(data["vote"], 2)
        self.assertEqual(data["is_accepted"], False)
        self.assertEqual(data["comment_count"], 0)

        response = self.client.put(
            f"/answer/{answer.id}/",
            json.dumps({"content": ""}),
            HTTP_AUTHORIZATION=self.eldpswp99_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assert_in_answer_info(data)
        self.assertEqual(data["content"], "world")
        self.assertEqual(data["vote"], 2)
        self.assertEqual(data["is_accepted"], False)
        self.assertEqual(data["comment_count"], 0)
        self.check_db_count()

    def test_put_answer_answer_id(self):
        answer = Answer.objects.get(content="world")

        response = self.client.put(
            f"/answer/{answer.id}/",
            json.dumps(
                {
                    # except content must be ignored
                    "vote": 2,
                    "content": "hello",
                    "is_accepted": True,
                    "is_active": False,
                    "created_at": "3:00",
                }
            ),
            HTTP_AUTHORIZATION=self.eldpswp99_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assert_in_answer_info(data)
        self.assertEqual(data["content"], "hello")
        self.assertEqual(data["vote"], 2)
        self.assertEqual(data["is_accepted"], False)
        self.assertEqual(data["comment_count"], 0)
        self.check_db_count()


class DeleteAnswerTestCase(UserQuestionTestSetting):
    client = Client()

    def check_db_count(self, **kwargs):
        answer_count = kwargs.get("answer_count", 1)
        deleted_answer_count = kwargs.get("deleted_answer_count", 0)

        super().check_db_count(answer_count=answer_count)
        self.assertEqual(
            Answer.objects.filter(is_active=False).count(), deleted_answer_count
        )

    def setUp(self):
        self.set_up_user_question()
        eldpswp99 = User.objects.get(username="eldpswp99")
        question = Question.objects.get(title="Hello")
        Answer.objects.create(user=eldpswp99, question=question, content="world")

    def test_delete_answer_answer_id_invalid_token(self):
        answer = Answer.objects.get(content="world")

        response = self.client.delete(f"/answer/{answer.id}/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(
            f"/answer/{answer.id}/",
            HTTP_AUTHORIZATION="asdf",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.check_db_count()

    def test_put_answer_answer_id_invalid_id(self):
        response = self.client.delete(
            f"/answer/-1/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_answer_answer_id_not_allowed_user(self):
        answer = Answer.objects.get(content="world")

        response = self.client.delete(
            f"/answer/{answer.id}/",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.check_db_count()

    def test_delete_answer_answer_id(self):
        answer = Answer.objects.get(content="world")

        response = self.client.delete(
            f"/answer/{answer.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        answer = Answer.objects.get(content="world")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(answer.is_active, False)
        self.check_db_count(deleted_answer_count=1)

    def test_delete_answer_answer_id_deleted_answer(self):
        answer = Answer.objects.get(content="world")
        answer.is_active = False
        answer.save()

        response = self.client.delete(
            f"/answer/{answer.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_answer_answer_id_twice(self):
        answer = Answer.objects.get(content="world")

        response = self.client.delete(
            f"/answer/{answer.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        answer = Answer.objects.get(content="world")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(answer.is_active, False)

        response = self.client.delete(
            f"/answer/{answer.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        answer = Answer.objects.get(content="world")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(answer.is_active, False)

        self.check_db_count(deleted_answer_count=1)

    def test_delete_answer_answer_id_accetped_answer(self):
        answer = Answer.objects.get(content="world")
        answer.is_accepted = True
        answer.save()

        response = self.client.delete(
            f"/answer/{answer.id}/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AnswerAcceptionTestCase(UserQuestionTestSetting):
    def assert_in_data(self, data):
        self.assertIn("question_id", data)
        self.assertIn("has_accepted", data)
        self.assertIn("answer_id", data)
        self.assertIn("is_accepted", data)

    def check_db_count(self, **kwargs):
        answer_count = kwargs.get("answer_count", 2)

        super().check_db_count(answer_count=answer_count)

    def setUp(self):
        self.set_up_user_question()
        qwerty = User.objects.get(username="qwerty")
        question = Question.objects.get(title="Hello")

        for answer in range(2):
            Answer.objects.create(user=qwerty, question=question, content=str(answer))

    def check_reputation(self, eldpswp99_reputation=0, qwerty_reputation=1234):
        eldpswp99_profile = User.objects.get(username="eldpswp99").profile
        self.assertEqual(eldpswp99_profile.reputation, eldpswp99_reputation)
        qwerty_profile = User.objects.get(username="qwerty").profile
        self.assertEqual(qwerty_profile.reputation, qwerty_reputation)


class PostAcceptionTestCase(AnswerAcceptionTestCase):
    client = Client()

    def test_post_answer_answer_id_accpetion_invalid_token(self):
        answer = Answer.objects.get(content="0")

        response = self.client.post(f"/answer/{answer.id}/acception/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION="asdf",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.check_db_count()
        self.check_reputation()

    def test_post_answer_answer_id_acception_invalid_id(self):
        response = self.client.post(
            f"/answer/-1/acception/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_reputation()

    def test_post_answer_answer_id_acception_deleted_answer(self):
        answer = Answer.objects.get(content="0")
        answer.is_active = False
        answer.save()

        response = self.client.post(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_reputation()

    def test_post_answer_answer_id_acception_not_allowed_user(self):
        answer = Answer.objects.get(content="0")

        response = self.client.post(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.check_db_count()
        self.check_reputation()

    def test_post_answer_answer_id_acception_already_accepted(self):
        answer = Answer.objects.get(content="0")
        answer.is_accepted = True
        answer.save()
        question = answer.question
        question.has_accepted = True
        question.save()
        answer_user_profile = answer.user.profile
        question_user_profile = question.user.profile
        question_user_profile.reputation += 2
        answer_user_profile.reputation += 15
        answer_user_profile.save()
        question_user_profile.save()

        response = self.client.post(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()
        self.check_reputation(eldpswp99_reputation=2, qwerty_reputation=1249)

    def test_post_answer_answer_id_acception_twice(self):
        answer = Answer.objects.get(content="0")
        question = answer.question

        response = self.client.post(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["question_id"], question.id)
        self.assertEqual(data["has_accepted"], True)
        self.assertEqual(data["answer_id"], answer.id)
        self.assertEqual(data["is_accepted"], True)
        self.check_reputation(eldpswp99_reputation=2, qwerty_reputation=1249)

        response = self.client.post(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        eldpswp99_profile = User.objects.get(username="eldpswp99").profile

        self.check_db_count()
        self.check_reputation(eldpswp99_reputation=2, qwerty_reputation=1249)

    def test_post_answer_answer_id_acception(self):
        answer = Answer.objects.get(content="0")
        eldpswp99_profile = answer.question.user.profile
        eldpswp99_profile.reputation = 123
        eldpswp99_profile.save()
        question = answer.question

        response = self.client.post(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["question_id"], question.id)
        self.assertEqual(data["has_accepted"], True)
        self.assertEqual(data["answer_id"], answer.id)
        self.assertEqual(data["is_accepted"], True)
        self.check_reputation(eldpswp99_reputation=125, qwerty_reputation=1249)


class DeleteAcceptionTestCase(AnswerAcceptionTestCase):
    client = Client()

    def check_reputation(self, eldpswp99_reputation=2, qwerty_reputation=1249):
        super().check_reputation(
            eldpswp99_reputation=eldpswp99_reputation,
            qwerty_reputation=qwerty_reputation,
        )

    def setUp(self):
        super().setUp()
        answer = Answer.objects.get(content="0")
        answer.is_accepted = True
        answer.save()
        question = answer.question
        question.has_accepted = True
        question.save()
        answer_user_profile = answer.user.profile
        answer_user_profile.reputation += 15
        answer_user_profile.save()
        question_user_profile = question.user.profile
        question_user_profile.reputation += 2
        question_user_profile.save()

    def test_delete_answer_answer_id_accpetion_invalid_token(self):
        answer = Answer.objects.get(content="0")

        response = self.client.delete(f"/answer/{answer.id}/acception/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION="asdf",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.check_db_count()
        self.check_reputation()

    def test_delete_answer_answer_id_acception_invalid_id(self):
        response = self.client.delete(
            f"/answer/-1/acception/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_reputation()

    def test_delete_answer_answer_id_acception_deleted_answer(self):
        answer = Answer.objects.get(content="0")
        answer.is_active = False
        answer.save()

        response = self.client.delete(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.check_reputation()

    def test_delete_answer_answer_id_acception_not_allowed_user(self):
        answer = Answer.objects.get(content="0")

        response = self.client.delete(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION=self.qwerty_token,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.check_db_count()
        self.check_reputation()

    def test_delete_answer_answer_id_acception_not_accepted(self):
        answer = Answer.objects.get(content="1")

        response = self.client.delete(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_db_count()
        self.check_reputation()

    def test_delete_answer_answer_id_acception_twice(self):
        answer = Answer.objects.get(content="0")
        question = answer.question

        response = self.client.delete(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["question_id"], question.id)
        self.assertEqual(data["has_accepted"], False)
        self.assertEqual(data["answer_id"], answer.id)
        self.assertEqual(data["is_accepted"], False)

        self.check_reputation(eldpswp99_reputation=0, qwerty_reputation=1234)
        response = self.client.delete(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_profile = User.objects.get(username="eldpswp99").profile
        self.assertEqual(user_profile.reputation, 0)
        self.check_db_count()
        self.check_reputation(eldpswp99_reputation=0, qwerty_reputation=1234)

    def test_delete_answer_answer_id_acception(self):
        answer = Answer.objects.get(content="0")
        question = answer.question
        user_profile = answer.user.profile
        user_profile.reputation = 123
        user_profile.save()

        response = self.client.delete(
            f"/answer/{answer.id}/acception/",
            HTTP_AUTHORIZATION=self.eldpswp99_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["question_id"], question.id)
        self.assertEqual(data["has_accepted"], False)
        self.assertEqual(data["answer_id"], answer.id)
        self.assertEqual(data["is_accepted"], False)

        self.check_reputation(eldpswp99_reputation=0, qwerty_reputation=108)
