# HabitTracker

**Многофункциональный трекер привычек с Django REST Framework, Celery, JWT и интеграцией Telegram.**

---

## Быстрый старт

### 1. Клонирование

~~~
git clone https://github.com/natali83911/habittracker.git
cd habittracker
~~~

### 2. Подготовка окружения

~~~
python -m venv .venv
source .venv/bin/activate # Linux/Mac
..venv\Scripts\activate # Windows

pip install -r requirements.txt
~~~

### 3. Миграции и суперюзер

~~~
python manage.py migrate
python manage.py createsuperuser
~~~

### 4. Запуск сервера

~~~
python manage.py runserver
~~~

### 5. Запуск с Gunicorn + Eventlet (для async/telegram/celery)

~~~
gunicorn -k eventlet config.wsgi:application
~~~


- В `config/wsgi.py` первой строкой:
import eventlet; eventlet.monkey_patch()

---
## Особенности
- Python 3.12
- Django 5.2
- Django REST Framework
- PostgreSQL

## Основные приложения

- **users** — регистрация/логин с JWT, работа профиля, Telegram ID, права доступа.
- **habits** — CRUD привычек, периодичность, напоминания, интеграция с celery.
- **Celery** — фоновая отправка уведомлений (например, Telegram).
- **JWT** — авторизация через токены.
- **Phonenumber** — поддержка телефонов в профиле.

---

## API Endpoints

- `POST /users/register/` — регистрация нового пользователя
- `POST /users/login/` — аутентификация, получение JWT
- `POST /users/token/refresh/` — обновление JWT
- `GET/PATCH /users/user/` — просмотр и изменение профиля
- `POST /users/tg-profile/` — создание Telegram профиля
- `GET /habits/` — список привычек (требует авторизации)
- `POST /habits/` — создать привычку
- `DELETE /users/deactivate/` — деактивация пользователя

---

## Тестирование

- Юнит‑ и интеграционные тесты:  

~~~
python manage.py test
~~~

- Покрытие

~~~
coverage run manage.py test
coverage report -m
coverage html
~~~


---

## Примеры запроса

### Регистрация

~~~
POST /users/register/
Content-Type: application/json
{
"email": "user@mail.com",
"password": "strongpass123",
"password2": "strongpass123"
}
~~~


### Получение и обновление профиля

~~~
GET /users/user/ # JWT обязательно
PATCH /users/user/
{
"city": "Москва",
"time_zone": "Europe/Moscow"
}
~~~


---

## Celery/Telegram

- Для отправки уведомлений по привычке запускаются задачи celery.
- Telegram‑бот интегрируется через chat_id и API.

---

## Лицензия

MIT License

---


