from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from habits.models import Habit
from habits.permissions import IsOwnerOrReadOnly
from habits.serializers import HabitSerializer
from habits.tasks import send_reminder
from users.models import UserTelegram

User = get_user_model()


# Тест моделей: Habit
class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="testuser@mail.com", password="123")

    def test_reward_and_related_validation(self):
        habit = Habit(
            user=self.user,
            action="Test",
            time="12:00",
            place="Дом",
            periodicity=1,
            reward="сладкое",
            duration=60,
        )
        habit.full_clean()
        Habit.objects.create(
            user=self.user,
            action="Walk",
            time="08:00",
            place="Улица",
            periodicity=2,
            is_pleasant=True,
            duration=30,
        )
        habit.related_habit = Habit.objects.first()
        with self.assertRaises(ValidationError):
            habit.full_clean()


# Тест сериализатора (API)
class HabitSerializerTest(APITestCase):
    def setUp(self):
        self.user = self.create_user()
        self.client.force_authenticate(self.user)

    def create_user(self):
        return User.objects.create_user(email="testuser@mail.com", password="123")

    def test_serializer_invalid_reward_and_related(self):
        pleasant_habit = Habit.objects.create(
            user=self.user,
            action="Дышать",
            time="10:10",
            place="Двор",
            periodicity=1,
            is_pleasant=True,
            duration=10,
        )
        data = {
            "user": self.user.id,
            "action": "Test",
            "time": "12:00",
            "place": "Дом",
            "periodicity": 1,
            "reward": "Конфета",
            "related_habit": pleasant_habit.id,
            "is_pleasant": False,
            "duration": 60,
            "is_public": False,
        }
        factory = APIRequestFactory()
        request = factory.post("/")
        request.user = self.user  # ключевой момент!
        serializer = HabitSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())


# Тест API: создание привычки
class HabitAPITest(APITestCase):
    def setUp(self):
        self.user = self.create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def create_user(self):
        return User.objects.create_user(email="apiuser@mail.com", password="123")

    def test_create_habit(self):
        url = reverse("habits:habit-list")
        data = {
            "action": "Учиться",
            "time": "10:00",
            "place": "Квартира",
            "periodicity": 2,
            "duration": 50,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)


# Permissions через TestCase
class PermissionTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(email="one@mail.com", password="123")
        self.user2 = User.objects.create(email="two@mail.com", password="123")
        self.habit = Habit.objects.create(
            user=self.user1,
            action="Тест",
            time="09:00",
            place="дом",
            periodicity=2,
            duration=60,
        )

    def test_owner_permission(self):
        perm = IsOwnerOrReadOnly()
        factory = APIRequestFactory()
        req = factory.get("/")
        req.user = self.user2
        self.assertFalse(perm.has_object_permission(req, None, self.habit))
        req.user = self.user1
        self.assertTrue(perm.has_object_permission(req, None, self.habit))


# Celery — unit test c моками (через TestCase)
class CeleryTaskTest(TestCase):
    @patch("habits.tasks.requests.post")
    def test_send_reminder(self, mock_post):
        user = User.objects.create(email="tguser@mail.com", password="123")
        tg = UserTelegram.objects.create(user=user, chat_id="111111")
        user.telegram_profile = tg
        user.save()
        habit = Habit.objects.create(
            user=user,
            action="Ping",
            time="06:00",
            place="дом",
            periodicity=1,
            duration=10,
        )
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "ok"
        send_reminder(habit.id)
        self.assertTrue(mock_post.called)
