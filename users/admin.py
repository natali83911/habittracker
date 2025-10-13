from django.contrib import admin

from .models import User, UserTelegram


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "phone_number", "city"]
    list_filter = ["city"]
    search_fields = ["email", "phone_number"]


@admin.register(UserTelegram)
class UserTelegramAdmin(admin.ModelAdmin):
    list_display = ["user", "chat_id", "telegram_username"]
    list_filter = ["user"]
    search_fields = ["user__email", "telegram_username"]
