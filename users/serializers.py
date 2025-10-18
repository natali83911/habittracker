from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import UserTelegram

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели пользователя для чтения информации.

    Включает основные данные, но id и время последней активности доступны только для чтения.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "avatar",
            "phone_number",
            "city",
            "motivation",
            "time_zone",
            "last_active",
        ]
        read_only_fields = ["id", "last_active"]


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления личных данных пользователя.

    Позволяет обновлять аватар, телефон, город, мотивацию и часовой пояс.
    """

    class Meta:
        model = User
        fields = ["avatar", "phone_number", "city", "motivation", "time_zone"]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор регистрации нового пользователя.

    Учитывает двойной ввод пароля, валидацию паролей и поля профиля.
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "password2", "avatar", "phone_number", "city")

    def validate(self, attrs):
        """
         Проверяет совпадение введённых паролей.

        Args:
            attrs (dict): Входные данные.

        Returns:
            dict: валидированные данные.

        Raises:
            serializers.ValidationError: если пароли не совпадают.
        """
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        """
        Создаёт пользователя с захешированным паролем.

        Args:
            validated_data (dict): валидированные профильные данные.

        Returns:
            User: новый пользователь.
        """
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserTelegramSerializer(serializers.ModelSerializer):
    """
    Сериализатор связи между пользователем и его Telegram-профилем.

    Включает связи, chat_id и username пользователя в Telegram.
    """

    class Meta:
        model = UserTelegram
        fields = ["id", "user", "chat_id", "telegram_username"]
        read_only_fields = ["id", "user"]
