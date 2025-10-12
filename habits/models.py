from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь - владелец привычки",
        help_text="Укажите владельца привычки",
    )

    action = models.CharField(
        max_length=255,
        verbose_name="Действие - что делать",
        help_text="Укажите действие",
    )

    time = models.TimeField(
        verbose_name="Время выполнения привычки",
        help_text="Укажите время, в которое выполняется привычка",
    )

    place = models.CharField(
        max_length=255,
        verbose_name="Место выполнения привычки",
        help_text="Укажите место выполнения",
    )

    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Периодичность выполнения привычки",
        help_text="Укажите периодичность выполнения привычки в днях (минимум 1, максимум 7)",
        validators=[MinValueValidator(1), MaxValueValidator(7)],
    )

    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Вознаграждение за выполнение привычки",
        help_text="Укажите вознаграждение за выполнение привычки",
    )

    related_habit = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"is_pleasant": True},
        related_name="pleasant_habits",
        verbose_name="Связанная приятная привычка (только приятные можно выбирать)",
        help_text="Сделайте выбор привычки",
    )

    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак, что привычка является приятной (а не полезной)",
        help_text="Сделайте выбор привычки",
    )

    duration = models.PositiveSmallIntegerField(
        help_text="Длительность в секундах, максимум 120",
        verbose_name="Время на выполнение привычки",
        validators=[MaxValueValidator(120)],
    )

    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности привычки (доступна другим пользователям для просмотра)",
        help_text="Сделайте выбор признака публичности привычки",
    )

    def clean(self):
        if self.reward and self.related_habit:
            raise ValidationError(
                "Нельзя одновременно указывать вознаграждение и связанную привычку."
            )
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )
        if self.duration > 120:
            raise ValidationError("Время выполнения не может быть больше 120 секунд.")
        if not (1 <= self.periodicity <= 7):
            raise ValidationError("Периодичность должна быть от 1 до 7 дней.")

    def __str__(self):
        return f"{self.action} в {self.time} в {self.place}"
