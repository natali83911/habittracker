from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    time = serializers.TimeField(format="%H:%M")
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
