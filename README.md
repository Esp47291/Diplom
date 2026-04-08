# Library Management API (DF1)

REST API для управления библиотекой: книги, авторы, пользователи, выдача книг.  
Стек: **Django 5**, **Django REST Framework**, **PostgreSQL**, **JWT**, **django-filter**, **drf-spectacular** (OpenAPI), **Docker**.

## Структура проекта

| Путь | Назначение |
|------|------------|
| `config/` | Настройки Django, корневые URL, WSGI |
| `accounts/` | Пользователи, роли, регистрация, JWT |
| `authors/` | Авторы |
| `books/` | Книги (связь с автором) |
| `loans/` | Выдачи книг и возврат |
| `tests/` | Pytest-тесты |
| `docker/` | Скрипт entrypoint для контейнера |
| `templates/`, `static/` | HTML-страницы и стили веб-интерфейса |

## Роли

- **Читатель (`reader`)** — регистрация по умолчанию; видит только свои выдачи; читает каталог книг и авторов.
- **Библиотекарь (`librarian`)** — CRUD авторов и книг; создаёт выдачи и отмечает возврат.
- **Администратор (`admin`)** — как библиотекарь; роль задаётся через админку или при создании суперпользователя.

Назначить пользователю роль библиотекаря: **Django Admin** → Users → поле `role`.

## Права доступа (коротко)

- **Пользователи**: список и чужие профили доступны только библиотекарю/админу. Любой авторизованный видит `/api/auth/users/me/`.
- **Авторы**: чтение доступно всем, создание/редактирование/удаление — любому авторизованному.
- **Книги**: чтение доступно всем, создание/редактирование — любому авторизованному. Удаление — только создателю книги или персоналу.
- **Выдачи**: любой авторизованный видит свои выдачи и может создавать/обновлять их; возврат доступен владельцу выдачи или персоналу.

## Запуск через Docker Compose

1. Скопируйте переменные окружения (при необходимости отредактируйте):

   ```bash
   copy .env.example .env
   ```

2. Соберите и поднимите сервисы:

   ```bash
   docker compose up --build
   ```

3. Сайт: `http://localhost:8000/` — главная, регистрация `/register/`, вход `/login/`, кабинет `/cabinet/` (редактирование имени и почты), памятка `/guide/`, FAQ `/faq/`, контакты `/contacts/`, схема `/diagram/`, проверка работы `/health/`. CSV выдач — из кабинета у библиотекаря.  
   API: Swagger `/api/docs/swagger/`. Админка: `http://localhost:8000/admin/` (создайте суперпользователя командой ниже).

Создание суперпользователя в контейнере:

```bash
docker compose exec web python manage.py createsuperuser
```

## Локальная разработка (без Docker)

Требуется установленный **PostgreSQL** и база `library` (или свои имя/пользователь в `.env`).

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

## Основные URL

| URL | Описание |
|-----|----------|
| `POST /api/auth/register/` | Регистрация (`username`, `email`, `password`, `password_confirm`) |
| `POST /api/auth/token/` | Получение JWT (`username`, `password`) |
| `POST /api/auth/token/refresh/` | Обновление access-токена |
| `GET /api/auth/users/me/` | Текущий пользователь (Bearer) |
| `GET /api/auth/users/` | Список пользователей (только библиотекарь/админ) |
| `GET/POST /api/authors/` | CRUD авторов (запись — любой авторизованный) |
| `GET/POST /api/books/` | CRUD книг (запись — любой авторизованный) |
| `GET/POST /api/loans/` | Выдачи (только для авторизованных) |
| `POST /api/loans/{id}/return/` | Возврат книги (владелец выдачи или персонал) |
| `GET /api/schema/` | OpenAPI схема |
| `GET /api/docs/swagger/` | Swagger UI |
| `GET /api/docs/redoc/` | ReDoc |

## Удобный Swagger

На странице Swagger (`/api/docs/swagger/`) есть блок **«Быстрый вход»**: вводите логин и пароль — токен подставляется автоматически, и можно сразу выполнять запросы.

## Каталог книг на сайте

- `GET /catalog/` — список книг (поиск по названию) + ссылки на Swagger и JSON.
- `GET /catalog/books/<id>/` — страница конкретной книги + ссылки на API.

## Демо-данные

Проект содержит миграцию `books/migrations/0003_seed_demo_books.py`, которая добавляет несколько авторов и книг **при первом запуске**, если книги в базе ещё не созданы.

## Поиск и фильтры

- **Книги** (`/api/books/`): параметры `search`, `title`, `genre`, `author`, `publication_year`, `ordering` и др. (см. `books/filters.py`).
- **Авторы** (`/api/authors/`): `first_name`, `last_name`, `birth_year`, `search`.
- **Выдачи** (`/api/loans/`): `status`, `book`, `user`, `issued_at__gte`, `issued_at__lte`.

Пример запроса с JWT:

```http
GET /api/books/?search=War&genre=novel
Authorization: Bearer <access_token>
```

## Тесты и покрытие

Используется SQLite в памяти (`config/settings_test.py`).

```bash
pytest tests/ -v --cov=accounts --cov=authors --cov=books --cov=loans --cov=config --cov-report=term-missing
```

## Требования к репозиторию

Инициализируйте Git и выложите код на GitHub/GitLab:

```bash
git init
git add .
git commit -m "Initial library API"
```

## PEP8

Рекомендуется проверка стиля, например:

```bash
pip install ruff
ruff check .
```
