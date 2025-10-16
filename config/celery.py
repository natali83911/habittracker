from __future__ import absolute_import, unicode_literals

import os

import eventlet
from celery import Celery

eventlet.monkey_patch()

# Установка переменной окружения для настроек проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Создание экземпляра Celery
app = Celery("config")

# Загрузка настроек из Django с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение задач в файлах tasks.py каждого приложения
app.autodiscover_tasks()
