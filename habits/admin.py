from django.contrib import admin
from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = [
        "id", "user", "action", "time", "place", "periodicity",
        "reward", "related_habit", "is_pleasant", "duration", "is_public"
    ]
    list_filter = ["is_pleasant", "is_public", "periodicity", "user"]
    search_fields = ["action", "reward", "user__email", "place"]
    ordering = ["user", "time"]
    readonly_fields = ["id"]

    fieldsets = (
        (None, {
            "fields": ("user", "action", "time", "place", "periodicity")
        }),
        ("Дополнительно", {
            "fields": ("reward", "related_habit", "is_pleasant", "duration", "is_public")
        }),
    )
