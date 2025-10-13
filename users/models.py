from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from config import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser должен иметь is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name="Почта")

    avatar = models.ImageField(
        upload_to="users/avatars/",
        verbose_name="Аватар",
        blank=True,
        null=True,
        default="users/avatars/default_avatar.png",
    )

    phone_number = PhoneNumberField(verbose_name="Телефон", blank=True, null=True)

    city = models.CharField(max_length=50, verbose_name="Город", blank=True, null=True)

    motivation = models.TextField(
        verbose_name="Мотивация",
        blank=True,
        null=True,
        help_text="Краткое описание или цель пользования трекером",
    )

    time_zone = models.CharField(
        max_length=50, verbose_name="Часовой пояс", default="UTC"
    )

    last_active = models.DateTimeField(
        verbose_name="Последняя активность", default=timezone.now
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class UserTelegram(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_profile",
        verbose_name="Пользователь - владелец привычки",
        help_text="Укажите пользователя",
    )
    chat_id = models.CharField(
        max_length=32,
        unique=True,
        verbose_name="Chat_id телеграм пользователя",
        help_text="Укажите chat_id телеграм пользователя",
    )
    telegram_username = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="Username телеграм пользователя",
        help_text="Укажите username телеграм пользователя",
    )

    class Meta:
        verbose_name = "Чат id телеграм"
        verbose_name_plural = "Чаты id телеграм"

    def __str__(self):
        return f"{self.user} ({self.chat_id})"
