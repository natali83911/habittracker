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
    try:
        habit = Habit.objects.get(id=habit_id)
        chat_id = habit.user.telegram_profile.chat_id
        text = f"Пора выполнить привычку: {habit.action}!"
        url = f"{settings.TELEGRAM_BOT_URL}{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

        # Явные логи окружения и параметров
        print("================== DEBUG BLOCK ==================")
        print(f".venv PATH: {settings.BASE_DIR}")
        print(f"URL: {url}")
        print(f"CHAT_ID: {chat_id}")
        print(f"TEXT: {text}")
        print("=================================================")

        # Проверка сети из celery worker
        try:
            net_resp = requests.get("https://api.telegram.org/")
            print(f"Network test (status): {net_resp.status_code}")
        except Exception as net_exc:
            print(f"Network test (error): {net_exc}")

        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(url, data=payload)
        print(f"Celery debug response: {response.status_code}, {response.text}")
    except Exception as e:
        print("Celery error:", e)


@shared_task
def check_and_send_reminders():
    now_dt = localtime(now())
    habits = Habit.objects.exclude(remind_at__isnull=True)
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
            from habits.tasks import send_reminder

            send_reminder.delay(habit.id)
            habit.last_reminded_at = now_dt
            habit.save()
