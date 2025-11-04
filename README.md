# HabitTracker

**Многофункциональный трекер привычек с Django REST Framework, Celery, JWT и интеграцией Telegram.**

---
## Развернутый сервер
Доступное API приложения
Swagger и схема: http://158.160.186.73:8000/schema/

## Требования
* Python 3.12+
* Docker, Docker Compose
* PostgreSQL, Redis (используется в контейнерах)
* Git

## Локальный запуск

### 1. Клонирование
~~~
git clone https://github.com/natali83911/habittracker.git
cd habittracker
~~~
### 2. Создание файла переменных окружения:

* Скопируйте .env.sample в .env и укажите свои значения:
~~~
cp .env.sample .env
~~~

* Обязательно заполните поле SECRET_KEY=.

### 3. Сборка и запуск контейнеров:
~~~
docker compose up -d --build
~~~

### 4. Запуск и миграция базы данных:
~~~
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
~~~

### 5. Дефолтный суперюзер (если нужно):
~~~
docker compose exec web python manage.py createsuperuser
~~~

### 6. Доступ к API и админке:

Админка: http://localhost:8000/admin/

API: http://localhost:8000/habits/
---

## Деплой на сервер

### 1. Подключение к серверу:
~~~
ssh <USER>@<SERVER_IP>
cd /home/<USER>/habittracker
~~~

### 2.  Получение последних изменений:
~~~
git pull origin main
~~~

### 3. Обновление контейнеров:
~~~
docker compose down
docker compose up -d --build
~~~

### 4. Миграции и статические файлы:
~~~
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
~~~
---

## Авторизация в API

* Для большинства запросов нужен JWT-токен.

* Получение токена:
~~~
POST /api/token/
Content-Type: application/json

{
  "email": "<email>",
  "password": "<password>"
}
~~~

* Использование токена во всех запросах:
~~~
Authorization: Bearer <ваш_access_token>
~~~

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

## CI/CD (GitHub Actions)
Процесс полностью автоматизирован:

* Запуск при пуше в ветки main, feature_final, develop
* Проверка и сборка:
  1. Линтинг (flake8)
  2. Запуск тестов через Django manage.py test
  3. Сборка docker-образов

* Автоматический деплой:
  * По SSH, с помощью секретного ключа GitHub Actions
  * Остановка старых контейнеров и запуск новых с актуальным кодом

Необходимые Secrets в GitHub:
* DJANGO_SECRET_KEY — секретный ключ Django
* SERVER_HOST — IP-адрес сервера
* SERVER_USER — имя пользователя на сервере
* SERVER_SSH_KEY — приватный SSH-ключ для доступа
---

# Инструкция по настройке сервера для CI/CD
1. Генерация SSH-ключа для GitHub Actions:
~~~
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy"
~~~

2. Добавьте публичный ключ в файл ~/.ssh/authorized_keys на сервере.
3. Загрузите приватный ключ в секцию Secrets GitHub Actions как SERVER_SSH_KEY.
4. В workflow .github/workflows/ci-cd.yml обязательно проверьте путь к проекту для шага деплоя!
---

## Дополнительно
* Swagger-схема API: http://158.160.186.73:8000/schema/
* Пример .env (настройка для локального теста):
~~~
SECRET_KEY=your_secret_key
DEBUG=True
POSTGRES_DB=habittracker
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
...
~~~ 
---

## Тесты
Запускаются автоматом через GitHub Actions и вручную:
~~~
docker compose exec web python manage.py test
~~~
---

### Полезные команды для контейнеров
* Стоп: docker compose down
* Запуск: docker compose up -d --build
* Логи: docker compose logs -f web
* Посмотреть контейнеры: docker compose ps
---

## Лицензия

MIT License

---


