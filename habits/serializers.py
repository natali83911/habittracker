from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Habit.

    Позволяет создавать, обновлять и валидировать привычки.
    Поля:
        - user: скрытое поле, текущий юзер (для создания привычки).
        - owner_email: email владельца привычки (только для чтения).
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owner_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "action",
            "time",
            "place",
            "periodicity",
            "reward",
            "related_habit",
            "is_pleasant",
            "duration",
            "is_public",
            "owner_email",
        ]

    def validate(self, data):
        """
        Выполняет комплексную валидацию создаваемой/обновляемой привычки.

        Проверки:
          - Нельзя одновременно указать и "reward", и "related_habit".
          - Приятная привычка не может иметь вознаграждение или связанную привычку.
          - Длительность не должна превышать 120 секунд.
          - Периодичность от 1 до 7 дней.

        Args:
            data (dict): входные данные привычки

        Returns:
            dict: очищенные и валидные данные

        Raises:
            serializers.ValidationError: если нарушено бизнес-правило.
        """
        reward = data.get("reward")
        related_habit = data.get("related_habit")
        is_pleasant = data.get("is_pleasant", False)
        duration = data.get("duration")

        if reward and related_habit:
            raise serializers.ValidationError(
                "Укажите либо вознаграждение, либо связанную привычку, но не оба одновременно."
            )
        if is_pleasant and (reward or related_habit):
            raise serializers.ValidationError(
                "Приятная привычка не может иметь вознаграждение или связанную привычку."
            )
        if duration and duration > 120:
            raise serializers.ValidationError(
                "Длительность не может превышать 120 секунд."
            )
        periodicity = data.get("periodicity", 1)
        if not (1 <= periodicity <= 7):
            raise serializers.ValidationError(
                "Периодичность должна быть от 1 до 7 дней."
            )
        return data
