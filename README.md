# FastAPI Ads API

Сервис объявлений купли/продажи с аутентификацией, ролями (`USER`/`ADMIN`) и разграничением прав.  
Реализован на **FastAPI** с асинхронной SQLite, JWT, пагинацией. Докеризирован.

## 🚀 Возможности

### Пользователи и авторизация
- Регистрация `POST /user/` (доступно всем)
- Авторизация `POST /auth/login` (JWT, срок действия 48 часов)
- Просмотр профиля `GET /user/{id}` (доступно всем)
- Список всех пользователей `GET /user/` (только `ADMIN`)
- Обновление/удаление своего профиля `PATCH /user/{id}`, `DELETE /user/{id}`
- Администратор может обновлять/удалять любого пользователя

### Объявления
- Создание `POST /advertisement/` (только авторизованные)
- Получение по ID `GET /advertisement/{id}` (доступно всем)
- Обновление/удаление своего объявления (`PATCH`, `DELETE`)
- Администратор может изменять/удалять любые объявления
- Поиск с **пагинацией** и фильтрацией:
  - по заголовку (`title`)
  - по имени автора (`author_username`)
  - по диапазону цен (`price_min`, `price_max`)
  - параметры `limit` (макс. 100), `offset`
  - ответ содержит `items`, `total`, `limit`, `offset`, `next`, `prev`

## 🛠 Технологии

- FastAPI
- SQLAlchemy 2.0 (async)
- aiosqlite
- python-jose (JWT)
- passlib (хэширование)
- Uvicorn
- Docker
- python-dotenv

## 📁 Структура проекта

```
FastAPI_homework/
├── app.py                  # Точка входа
├── database.py             # Подключение к БД
├── models.py               # SQLAlchemy модели (User, Advertisement)
├── schemas.py              # Pydantic схемы
├── security.py             # JWT, хэширование, зависимости
├── routers/
│   ├── __init__.py
│   ├── auth.py             # POST /auth/login
│   ├── user.py             # CRUD пользователей
│   └── advertisement.py    # CRUD объявлений + поиск
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

## 📦 Установка и запуск (локально)

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/bsekinaev/FastAPI_homework.git
   cd FastAPI_homework
   ```

2. **Создайте виртуальное окружение**
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Linux/Mac
   .venv\Scripts\activate         # Windows
   ```

3. **Установите зависимости**
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте переменные окружения**
   Скопируйте `.env.example` в `.env` и при необходимости измените секретный ключ:
   ```bash
   cp .env.example .env
   ```
   Содержимое `.env`:
   ```ini
   SECRET_KEY=super_secret
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_HOURS=48
   DATABASE_URL=sqlite+aiosqlite:///./ads.db
   ```

5. **Запустите приложение**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
   API документация: `http://localhost:8000/docs`

## 🐳 Запуск через Docker

1. **Соберите образ**
   ```bash
   docker build -t fastapi-ads .
   ```

2. **Запустите контейнер**
   ```bash
   docker run -p 8000:8000 --env-file .env fastapi-ads
   ```

## 🧪 Тестирование API (примеры cURL)

### Регистрация и логин
```bash
# Создать пользователя
curl -X POST "http://localhost:8000/user/" \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"user123"}'

# Получить JWT-токен
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"user123"}'
# В ответе будет {"access_token":"...","token_type":"bearer"}
```

### Создание объявления (требуется токен)
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -X POST "http://localhost:8000/advertisement/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Велосипед","description":"Горный","price":15000}'
```

### Получение объявления (без токена)
```bash
curl "http://localhost:8000/advertisement/1"
```

### Поиск с пагинацией и фильтром по автору
```bash
curl "http://localhost:8000/advertisement/?author_username=user1&limit=5&offset=0"
```

### Обновление своего объявления
```bash
curl -X PATCH "http://localhost:8000/advertisement/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"price":14000}'
```

### Администратор: список всех пользователей
```bash
# Под администратором создаётся автоматически при запуске (логин: admin, пароль: admin)
ADMIN_TOKEN="..."
curl -X GET "http://localhost:8000/user/" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Удаление объявления
```bash
curl -X DELETE "http://localhost:8000/advertisement/1" \
  -H "Authorization: Bearer $TOKEN"
```

## ⚙️ Примечания

- При первом запуске автоматически создаётся пользователь `admin` с паролем `admin` и ролью `ADMIN`.
- Пароли хэшируются (используется `sha256_crypt`).
- Токен истекает через 48 часов.
- При недостатке прав или отсутствии токена возвращаются коды `401` или `403`.
- Все эндпоинты полностью асинхронны.
