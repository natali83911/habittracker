from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase

from users.models import UserTelegram
from users.permissions import IsOwner
from users.serializers import RegisterSerializer, UserTelegramSerializer

# Тест модели User и UserTelegram
User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email="foo@mail.com", password="1234")
        self.assertEqual(user.email, "foo@mail.com")
        self.assertTrue(user.check_password("1234"))
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(email="admin@mail.com", password="super")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_usertelegram_link(self):
        user = User.objects.create_user(email="tg@example.com", password="x")
        tg = UserTelegram.objects.create(
            user=user, chat_id="333", telegram_username="tester"
        )
        self.assertEqual(str(tg), f"{user} (333)")


# Тест сериализаторов — регистрация, деталка, telegram-профиль
class UserSerializerTest(APITestCase):
    def test_register_serializer_validation(self):
        data = {
            "email": "reg@mail.com",
            "password": "1234test",
            "password2": "1234test",
            "city": "Москва",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, "reg@mail.com")

    def test_register_serializer_password_mismatch(self):
        data = {"email": "fail@mail.com", "password": "pass", "password2": "other"}
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_user_serializer(self):
        self.client.force_authenticate(
            User.objects.create_user(email="u@mail.com", password="xxx")
        )
        response = self.client.get("/users/user/")
        self.assertEqual(response.status_code, 200)

    def test_user_telegram_serializer(self):
        user = User.objects.create_user(email="tg2@mail.com", password="ppp")
        tg = UserTelegram.objects.create(user=user, chat_id="555")
        serializer = UserTelegramSerializer(tg)
        data = serializer.data
        self.assertEqual(data["chat_id"], "555")


# Тест API (ViewSet) для User и UserTelegram
class UserAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="api@mail.com", password="api123")
        self.client.force_authenticate(self.user)

    def test_user_detail(self):
        url = reverse("users:user_detail")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["email"], self.user.email)

    def test_update_profile(self):
        url = reverse("users:user_detail")
        resp = self.client.patch(url, {"city": "Новосибирск"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["city"], "Новосибирск")

    def test_register(self):
        self.client.logout()
        url = reverse("users:register")
        data = {
            "email": "new@mail.com",
            "password": "123passQ",
            "password2": "123passQ",
        }
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(User.objects.filter(email="new@mail.com").exists())

    def test_create_tg_profile(self):
        url = reverse("users:telegram-profile-list")
        resp = self.client.post(url, {"chat_id": "999", "telegram_username": "tg_user"})
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(
            UserTelegram.objects.filter(user=self.user, chat_id="999").exists()
        )


# Тест прав доступа
class UserTelegramPermissionTest(TestCase):
    def test_owner_permission(self):
        user1 = User.objects.create_user(email="per1@mail.com", password="111")
        user2 = User.objects.create_user(email="per2@mail.com", password="222")
        tg = UserTelegram.objects.create(user=user1, chat_id="321")
        perm = IsOwner()
        factory = APIRequestFactory()
        req = factory.get("/")
        req.user = user2
        self.assertFalse(perm.has_object_permission(req, None, tg))
        req.user = user1
        self.assertTrue(perm.has_object_permission(req, None, tg))
