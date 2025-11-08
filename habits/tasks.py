# from celery import shared_task
# import requests
# from django.conf import settings
# from habits.models import Habit
#
#
# @shared_task
# def send_reminder(habit_id):
#     habit = Habit.objects.get(id=habit_id)
#     chat_id = habit.user.telegram_profile.chat_id
#     text = f"Пора выполнить привычку: {habit.action}!"
#     url = f"{settings.TELEGRAM_BOT_URL}{settings.TELEGRAM_BOT_TOKEN}/sendMessage"#
#     requests.post(url, data={'chat_id': chat_id, 'text': text})


import requests
from celery import shared_task
from django.conf import settings
from django.utils.timezone import localtime, now, timedelta

from habits.models import Habit


@shared_task
def send_reminder(habit_id):
    """
    Отправляет напоминание по привычке в Telegram или другой канал.
    :param habit_id: идентификатор привычки для напоминания.
    """
    try:
        habit = Habit.objects.get(id=habit_id)
        if (
            not hasattr(habit.user, "telegram_profile")
            or habit.user.telegram_profile is None
        ):
            print(f"No telegram profile for user {habit.user.email}")
            return

        chat_id = habit.user.telegram_profile.chat_id
        text = f"Пора выполнить привычку: {habit.action}!"
        url = f"{settings.TELEGRAM_BOT_URL}{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

        print("================== DEBUG BLOCK ==================")
        print(f".venv PATH: {settings.BASE_DIR}")
        print(f"URL: {url}")
        print(f"CHAT_ID: {chat_id}")
        print(f"TEXT: {text}")
        print("=================================================")

        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=payload)
        print(f"Celery debug response: {response.status_code}, {response.text}")
    except Exception as e:
        print("Celery error:", e)


@shared_task
def check_and_send_reminders():
    """
    Проверяет все привычки пользователей и отправляет напоминания, если наступило время.

    Основная логика:
    - сравнение времени remind_at с now_dt;
    - повторные напоминания по repeat;
    - постановка задачи в очередь через Celery.

    """
    now_dt = localtime(now())
    habits = Habit.objects.exclude(remind_at__isnull=True)
    print(f"Проверка напоминаний для {habits.count()} привычки в {now_dt}")

    for habit in habits:
        print(f"Проверка привычки id={habit.id}")
        print(
            f"remind_at={habit.remind_at}, "
            f"repeat={habit.repeat}, "
            f"last_reminded_at={habit.last_reminded_at}, "
            f"now_dt={now_dt}"
        )

    for habit in habits:
        to_remind = False
        if not habit.last_reminded_at and habit.remind_at <= now_dt:
            to_remind = True
        elif habit.repeat == "daily" and habit.last_reminded_at:
            next_time = habit.last_reminded_at + timedelta(days=1)
            if now_dt >= next_time:
                to_remind = True
        elif habit.repeat == "weekly" and habit.last_reminded_at:
            next_time = habit.last_reminded_at + timedelta(weeks=1)
            if now_dt >= next_time:
                to_remind = True

        if to_remind:
            print(f"Поставлено в очередь напоминание о привычке {habit.id}")
            from habits.tasks import send_reminder

            send_reminder.delay(habit.id)
            # Обновляем last_reminded_at только если успешно задание отправлено в очередь
            habit.last_reminded_at = now_dt
            habit.save()
