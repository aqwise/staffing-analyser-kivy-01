# Staffing Analyzer API

FastAPI приложение для анализа запросов на подбор персонала с использованием Google GenAI.

## Структура проекта

```
staffing_analyzer/
├── app/                    # FastAPI приложение
│   ├── __init__.py
│   ├── main.py            # Основное приложение и эндпоинты
│   ├── models.py          # Pydantic модели
│   ├── services.py        # Бизнес-логика
│   ├── config.py          # Конфигурация
│   └── backend_logic.py   # Логика, украденная из легаси варианта
├── legacy/                # Существующий код
│   └── logic.py          # Legacy логика анализа
├── requirements.txt       # Зависимости
├── requirements-dev.txt   # Зависимости для разработки
├── .env.example          # Пример переменных окружения
└── run.py                # Запуск приложения
```

## Установка и запуск

1. Создать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Создать .env файл на основе .env.example:
```bash
cp ../.env.example ../.env
```

4. Заполнить GOOGLE_API_KEY в .env файле

5. Запустить приложение (открывайте сваггер http://localhost:8000/docs#/):
```bash
python ../run.py
```

## API Эндпоинты

- `GET /` - Информация об API
- `GET /health` - Health check
- `POST /api/v1/analyze` - Анализ текста
- `GET /api/v1/status` - Статус API
- `GET /docs` - Swagger документация
- `GET /redoc` - ReDoc документация

## Пример использования

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "query": "Нужен Python разработчик с опытом 3+ года",
        "api_key": "your-google-api-key"
    }
)

result = response.json()
print(result["result"])
```

Запуск с автоперезагрузкой (открывайте сваггер http://localhost:8000/docs#/):
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
