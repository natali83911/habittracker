from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from config import settings


class UserManager(BaseUserManager):
    """
    Кастомный менеджер пользователей.

    Реализует:
      - Создание обычного пользователя по email и паролю.
      - Создание суперпользователя с флагами is_staff и is_superuser.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет обычного пользователя с указанным email и паролем.

        Args:
            email (str): Email пользователя (обязателен).
            password (str): Пароль.
            **extra_fields: Дополнительные поля профиля.

        Returns:
            User: созданный пользователь.

        Raises:
            ValueError: если email не указан.
        """
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Создает и сохраняет суперпользователя с email и паролем.

        Устанавливает флаги is_staff и is_superuser (True).
        Проверяет корректность флагов.

        Args:
            email (str): Email суперпользователя.
            password (str): Пароль.
            **extra_fields: Дополнительные поля.

        Returns:
            User: созданный суперпользователь.

        Raises:
            ValueError: если is_staff или is_superuser не True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser должен иметь is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Модель пользователя без username, с email как идентификатором.

    Поля:
        email (EmailField): Логин и идентификатор пользователя.
        avatar (ImageField): Аватар пользователя.
        phone_number (PhoneNumberField): Телефон пользователя.
        city (CharField): Город пользователя.
        motivation (TextField): Описание мотивации или цели пользования трекером.
        time_zone (CharField): Часовой пояс пользователя.
        last_active (DateTimeField): Последняя активность.
    """

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
        """
        Строковое представление пользователя.

        Returns:
            str: email пользователя.
        """
        return self.email


class UserTelegram(models.Model):
    """
    Профиль Telegram для пользователя.

    Содержит связь с сущностью пользователя, chat_id и username телеграмма.
    """

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
        """
        Строковое представление Telegram-профиля.

        Returns:
            str: Представление в виде user (chat_id).
        """
        return f"{self.user} ({self.chat_id})"
