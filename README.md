# FastAPI приложение для работы с товарами

## Требования
- Python 3.8+
- Firebird Database
- Установленные зависимости из requirements.txt

## Установка
1. Скопируйте .env.example в .env и заполните настройки:
   ```bash
   cp .env.example .env
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Переменные окружения (.env)
- `DATABASE_URL` - URL подключения к Firebird
- `DEBUG` - Режим отладки (True/False)
- `SECRET_KEY` - Секретный ключ приложения
- `IMG_STORAGE_PATH` - Путь для хранения изображений

## Запуск
```bash
uvicorn app.main:app --reload
```

## Примеры API
- Получение списка товаров: `GET /products/`
- Загрузка изображения: `POST /modelgoods/image/`
- Проверка здоровья: `GET /healthcheck`
