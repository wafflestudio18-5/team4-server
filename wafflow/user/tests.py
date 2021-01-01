from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.authtoken.models import Token

from answer.models import Answer, UserAnswer
from comment.models import Comment
from question.models import Question, UserQuestion
from user.models import UserProfile

import json


class UserTestSetting(TestCase):
    def set_up_users(self):
        self.set_up_user_guzus()
        self.set_up_user_retired_guzus()
        self.set_up_user_eldpswp99()
        self.set_up_user_YeonghyeonKo()

    def set_up_user_guzus(self):
        self.guzus = User.objects.create_user(
            username="guzus", email="guzus@naver.com", password="password"
        )
        guzus_profile = UserProfile.objects.create(
            user=self.guzus,
            nickname="audrn31",
            title="grandmaster",
            intro="Hello World!",
        )
        Token.objects.create(user=self.guzus)
        self.guzus_token = "Token " + Token.objects.get(user=self.guzus).key

    def set_up_user_retired_guzus(self):
        self.retired_guzus = User.objects.create_user(
            username="RetiredGuzus",
            email="retired_guzus@naver.com",
            password="password",
            is_active=False,
        )
        retired_guzus_profile = UserProfile.objects.create(
            user=self.retired_guzus,
            nickname="RG",
            title="Grand Theft Auto!",
            intro="Hello Wafflow!",
        )
        Token.objects.create(user=self.retired_guzus)
        self.retired_guzus_token = (
            "Token " + Token.objects.get(user=self.retired_guzus).key
        )

    def set_up_user_eldpswp99(self):
        self.eldpswp99 = User.objects.create_user(
            username="eldpswp99", email="nrg1392@naver.com", password="password"
        )
        eldpswp99_profile = UserProfile.objects.create(
            user=self.eldpswp99,
            nickname="MyungHoon Park",
            intro="Hello World!",
        )
        Token.objects.create(user=self.eldpswp99)
        self.eldpswp99_token = "Token " + Token.objects.get(user=self.eldpswp99).key

    def set_up_user_YeonghyeonKo(self):
        self.YeonghyeonKo = User.objects.create_user(
            username="YeonghyeonKo", email="ko@naver.com", password="0000"
        )
        YeonghyeonKo_profile = UserProfile.objects.create(
            user=self.YeonghyeonKo,
            nickname="Yeonghyeon Ko",
            intro="Deploying is fun!",
        )
        Token.objects.create(user=self.YeonghyeonKo)
        self.YeonghyeonKo_token = (
            "Token " + Token.objects.get(user=self.YeonghyeonKo).key
        )

    def set_up_user_activites(self):
        self.guzus_QUESTION_COUNT = 45
        for i in range(self.guzus_QUESTION_COUNT):
            Question.objects.create(
                title=str(i + 1),
                content=str(i + 1),
                user=self.guzus,
                vote=i + 1,
            )
        Question.objects.create(
            title=str(self.guzus_QUESTION_COUNT + 1),
            content=str(self.guzus_QUESTION_COUNT + 1),
            user=self.guzus,
            vote=i + 1,
            is_active=False,
        )

        self.eldpswp99_ANSWER_COUNT = 30
        for i in range(self.eldpswp99_ANSWER_COUNT):
            Answer.objects.create(
                content=str(i + 1),
                question=Question.objects.get(id=i + 1),
                user=self.eldpswp99,
                vote=i + 1,
            )
        Answer.objects.create(
            content=str(self.eldpswp99_ANSWER_COUNT + 1),
            question=Question.objects.get(id=self.eldpswp99_ANSWER_COUNT + 1),
            user=self.eldpswp99,
            vote=i + 1,
            is_active=False,
        )

        self.YeonghyeonKo_BOOKMARK_COUNT = 15
        for i in range(self.YeonghyeonKo_BOOKMARK_COUNT):
            question = Question.objects.get(id=i + 1)
            UserQuestion.objects.create(
                user=self.YeonghyeonKo, question=question, bookmark=True, rating=0
            )

    def check_guzus(self, data):
        self.assertIn("id", data)
        self.assertEqual(data["username"], "guzus")
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertEqual(data["email"], "guzus@naver.com")
        self.assertIn("last_login", data)
        self.assertEqual(data["nickname"], "audrn31")
        self.assertIn("picture", data)
        self.assertEqual(data["reputation"], 0)
        self.assertEqual(data["title"], "grandmaster")
        self.assertEqual(data["intro"], "Hello World!")
        self.assertEqual(data["question_count"], 0)
        self.assertEqual(data["answer_count"], 0)
        self.assertEqual(data["bookmark_count"], 0)

    def check_guzus_after_activites(self, data):
        self.assertIn("id", data)
        self.assertEqual(data["username"], "guzus")
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertEqual(data["email"], "guzus@naver.com")
        self.assertIn("last_login", data)
        self.assertEqual(data["nickname"], "audrn31")
        self.assertIn("picture", data)
        self.assertEqual(data["reputation"], 0)
        self.assertEqual(data["title"], "grandmaster")
        self.assertEqual(data["intro"], "Hello World!")
        self.assertEqual(data["question_count"], self.guzus_QUESTION_COUNT)
        self.assertEqual(data["answer_count"], 0)
        self.assertEqual(data["bookmark_count"], 0)

    def check_eldpswp99_after_activites(self, data):
        self.assertIn("id", data)
        self.assertEqual(data["username"], "eldpswp99")
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertEqual(data["email"], "nrg1392@naver.com")
        self.assertIn("last_login", data)
        self.assertEqual(data["nickname"], "MyungHoon Park")
        self.assertIn("picture", data)
        self.assertEqual(data["reputation"], 0)
        self.assertIn("title", data)
        self.assertEqual(data["intro"], "Hello World!")
        self.assertEqual(data["question_count"], 0)
        self.assertEqual(data["answer_count"], self.eldpswp99_ANSWER_COUNT)
        self.assertEqual(data["bookmark_count"], 0)

    def check_YeonghyeonKo_after_activites(self, data):
        self.assertIn("id", data)
        self.assertEqual(data["username"], "YeonghyeonKo")
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertEqual(data["email"], "ko@naver.com")
        self.assertIn("last_login", data)
        self.assertEqual(data["nickname"], "Yeonghyeon Ko")
        self.assertIn("picture", data)
        self.assertEqual(data["reputation"], 0)
        self.assertIn("title", data)
        self.assertEqual(data["intro"], "Deploying is fun!")
        self.assertEqual(data["question_count"], 0)
        self.assertEqual(data["answer_count"], 0)
        self.assertEqual(data["bookmark_count"], self.YeonghyeonKo_BOOKMARK_COUNT)


class PostUserTestCase(UserTestSetting):
    client = Client()

    def setUp(self):
        self.set_up_user_guzus()

    def test_post_user_duplicated_value(self):
        # duplicated username
        response = self.client.post(
            "/user/",
            json.dumps(
                {
                    "username": "guzus",
                    "password": "1234",
                    "email": "audrn31@snu.ac.kr",
                    "nickname": "lionel messi",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # duplicated email
        response = self.client.post(
            "/user/",
            json.dumps(
                {
                    "username": "magnolia",
                    "password": "1234",
                    "email": "guzus@naver.com",
                    "nickname": "lionel messi",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # duplicated nickname
        response = self.client.post(
            "/user/",
            json.dumps(
                {
                    "username": "magnolia",
                    "password": "1234",
                    "email": "audrn31@snu.ac.kr",
                    "nickname": "audrn31",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_post_user_too_long_username(self):
        response = self.client.post(
            "/user/",
            json.dumps(
                {
                    "username": "a" * 20,
                    "password": "1234",
                    "email": "audrn31@snu.ac.kr",
                    "nickname": "lionel messi",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_post_user_incomplete_request(self):
        response = self.client.post(
            "/user/",
            json.dumps(
                {
                    "username": "magnolia",
                    "password": "1234",
                    "email": "audrn31@snu.ac.kr",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_post_user(self):
        response = self.client.post(
            "/user/",
            json.dumps(
                {
                    "username": "magnolia",
                    "password": "1234",
                    "email": "audrn31@snu.ac.kr",
                    "nickname": "lionel messi",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "magnolia")
        self.assertIn("token", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertEqual(data["email"], "audrn31@snu.ac.kr")
        self.assertIn("last_login", data)
        self.assertEqual(data["nickname"], "lionel messi")
        self.assertIn("picture", data)
        self.assertEqual(data["reputation"], 0)
        self.assertIn("title", data)
        self.assertIn("intro", data)
        self.assertEqual(data["question_count"], 0)
        self.assertEqual(data["answer_count"], 0)
        self.assertEqual(data["bookmark_count"], 0)

        user_count = User.objects.count()
        self.assertEqual(user_count, 2)
        user_profile_count = UserProfile.objects.count()
        self.assertEqual(user_profile_count, 2)


class GetUserMeTestCase(UserTestSetting):
    client = Client()

    def setUp(self):
        self.set_up_users()

    def test_get_user_me_invalid_pk(self):
        response = self.client.get(
            "/user/you/",
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(
            "/user/100/",
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_me_invalid_token(self):
        response = self.client.get(
            "/user/me/",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_me_deleted_user(self):
        response = self.client.get(
            "/user/me/",
            HTTP_AUTHORIZATION=self.retired_guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_me(self):
        response = self.client.get(
            "/user/me/",
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.check_guzus(data)


class GetUserUserIDTestCase(UserTestSetting):
    def setUp(self):
        self.set_up_users()

    def test_get_user_user_id_of_deleted_user(self):
        response = self.client.get(
            f"/user/{self.retired_guzus.id}/",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_user_id(self):
        response = self.client.get(
            f"/user/{self.guzus.id}/",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.check_guzus(data)

        response = self.client.get(
            f"/user/{self.guzus.id}/",
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.check_guzus(data)

        # response = self.client.get(
        #     f"/user/{self.guzus.id}/",
        #     HTTP_AUTHORIZATION=self.retired_guzus_token,
        #     content_type="application/json",
        # )

        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data = response.json()
        # self.check_guzus(data)

    def test_get_user_user_id_after_activites(self):
        self.set_up_user_activites()

        response = self.client.get(
            f"/user/{self.guzus.id}/",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.check_guzus_after_activites(data)

        response = self.client.get(
            f"/user/{self.eldpswp99.id}/",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.check_eldpswp99_after_activites(data)

        response = self.client.get(
            f"/user/{self.YeonghyeonKo.id}/",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.check_YeonghyeonKo_after_activites(data)


class PutUserMeTestCase(UserTestSetting):
    def setUp(self):
        self.set_up_users()

    def test_put_user_me_invalid_pk(self):
        response = self.client.put(
            "/user/you/",
            json.dumps({"password": "12345", "nickname": "Django"}),
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(
            f"/user/{self.guzus.id}/",
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_user_me_invalid_token(self):
        response = self.client.put(
            "/user/me/",
            json.dumps({"password": "12345", "nickname": "Django"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(
            "/user/me/",
            json.dumps({"password": "12345", "nickname": "Django"}),
            HTTP_AUTHORIZATION=self.retired_guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_user_me_too_long_nickname(self):
        response = self.client.put(
            "/user/me/",
            json.dumps({"password": "12345", "nickname": "n" * 17}),
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_user_me_duplicated_nickname(self):
        response = self.client.put(
            "/user/me/",
            json.dumps({"password": "12345", "nickname": "MyungHoon Park"}),
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_user_me_same_used_nickname(self):
        response = self.client.put(
            "/user/me/",
            json.dumps({"password": "12345", "nickname": "audrn31"}),
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.check_guzus(data)

    def test_put_user_me_try_change_username_or_email(self):
        response = self.client.put(
            "/user/me/",
            json.dumps({"password": "12345", "username": "new_guzus"}),
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(
            "/user/me/",
            json.dumps({"password": "12345", "email": "new_guzus@naver.com"}),
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_user_me(self):
        response = self.client.put(
            "/user/me/",
            json.dumps(
                {
                    "title": "hi",
                    "intro": "I'm waffle",
                    "password": "12345",
                    "nickname": "new_audrn31",
                }
            ),
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "guzus")
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertEqual(data["email"], "guzus@naver.com")
        self.assertIn("last_login", data)
        self.assertEqual(data["nickname"], "new_audrn31")
        self.assertIn("picture", data)
        self.assertEqual(data["reputation"], 0)
        self.assertEqual(data["title"], "hi")
        self.assertEqual(data["intro"], "I'm waffle")
        self.assertEqual(data["question_count"], 0)
        self.assertEqual(data["answer_count"], 0)
        self.assertEqual(data["bookmark_count"], 0)


class DeleteUserMeTestCase(UserTestSetting):
    def setUp(self):
        self.set_up_users()

    def test_delete_user_me_invalid_pk(self):
        response = self.client.delete(
            f"/user/{self.guzus.id}/",
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_me_invalid_token(self):
        response = self.client.delete(
            "/user/me/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(
            "/user/me/",
            HTTP_AUTHORIZATION=self.retired_guzus_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_me(self):
        response = self.client.delete(
            "/user/me/",
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PutUserLoginTestCase:
    def setUp(self):
        self.set_up_users()

    def test_put_user_login_invalid_info(self):
        response = self.client.put(
            "/user/login/",
            json.dumps({"username": "guzus", "password": "wrong_password"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_user_login_deleted_user(self):
        response = self.client.put(
            "/user/login/",
            json.dumps({"username": "retired_guzus", "password": "password"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_user_login_too_long_username(self):
        response = self.client.put(
            "/user/login/",
            json.dumps({"username": "1" * 17, "password": "password"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_user_login(self):
        response = self.client.put(
            "/user/login/",
            json.dumps({"username": "guzus", "password": "password"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.check_guzus(data)
        self.assertIn("token", data)


class PostUserLogoutTestCase(UserTestSetting):
    def setUp(self):
        self.set_up_users()

    def test_post_user_logout_invalid_token(self):
        response = self.client.post(
            "/user/logout/",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_user_logout(self):
        response = self.client.post(
            "/user/logout/",
            HTTP_AUTHORIZATION=self.guzus_token,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
