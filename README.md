
# FastAPI Ads API

Сервис объявлений купли/продажи, реализованный на **FastAPI** с асинхронной базой данных SQLite.  
Докеризирован, готов к запуску в контейнере.

## 🚀 Возможности
- Создание объявления (`POST /advertisement`)
- Обновление объявления (`PATCH /advertisement/{id}`)
- Удаление объявления (`DELETE /advertisement/{id}`)
- Получение объявления по ID (`GET /advertisement/{id}`)
- Поиск объявлений по полям (`GET /advertisement?title=&author=&price_min=&price_max=`)

## 🛠 Технологии
- FastAPI
- SQLAlchemy (async)
- aiosqlite
- Uvicorn
- Docker

## 📁 Структура проекта

```
FastAPI_homework/
├── app.py              # Основное приложение (роуты)
├── models.py           # SQLAlchemy и Pydantic модели
├── database.py         # Подключение к БД
├── requirements.txt    # Зависимости
├── Dockerfile          # Инструкция для Docker
├── .gitignore          # Игнорируемые файлы
└── README.md           # Документация
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

4. **Запустите приложение**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
   API будет доступно по адресу `http://localhost:8000`, документация – `http://localhost:8000/docs`.

## 🐳 Запуск через Docker

1. **Соберите образ**
   ```bash
   docker build -t fastapi-ads .
   ```

2. **Запустите контейнер**
   ```bash
   docker run -p 8000:8000 fastapi-ads
   ```

После запуска Swagger‑документация будет доступна по `http://localhost:8000/docs`.

## 🧪 Тестирование API (примеры cURL)

```bash
# Создать объявление
curl -X POST "http://localhost:8000/advertisement" \
  -H "Content-Type: application/json" \
  -d '{"title":"Велосипед","description":"Горный велосипед","price":15000,"author":"Иван"}'

# Получить объявление по id
curl "http://localhost:8000/advertisement/1"

# Обновить цену
curl -X PATCH "http://localhost:8000/advertisement/1" \
  -H "Content-Type: application/json" \
  -d '{"price":14000}'

# Поиск по автору и цене
curl "http://localhost:8000/advertisement?author=%D0%98%D0%B2%D0%B0%D0%BD&price_min=10000"

# Удалить объявление
curl -X DELETE "http://localhost:8000/advertisement/1" -v
```

