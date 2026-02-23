# Интеграционный веб-интерфейс для системы "Товар-Деньги-Товар"

Расширяет функционал базовой системы, добавляя:
- REST API для управления расширенными описаниями товаров
- Микросервис для загрузки и обработки изображений
- Интеграцию с внешними системами учета
- Расширенную аналитику продаж

❗ Внимание! Рекомендации по безопасности:
- Используйте исключительно в защищенных/закрытых сетях
- Требуется дополнительная настройка аутентификации для production
- Ограничьте доступ к API через firewall
- Регулярно обновляйте секретные ключи

## Требования
- Python 3.8.9 (рекомендуется для Windows)  
  Скачать: [python-3.8.9.exe](https://www.python.org/ftp/python/3.8.9/python-3.8.9.exe)  
  Все версии: [python.org/downloads/windows/](https://www.python.org/downloads/windows/)
- Firebird Database
- Установленные зависимости из requirements.txt

## Установка
1. Скопируйте .env.example в .env:
   ```bash
   cp .env.example .env
   ```
2. Настройте параметры подключения в .env
3. Установите зависимости:
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
# Стандартный запуск (если uvicorn доступен в PATH)
uvicorn app.main:app --reload

# Альтернативный способ запуска (если возникает ошибка "uvicorn не распознано")
python -m uvicorn app.main:app --reload --port 7990 --host 0.0.0.0

# Параметры запуска:
# --reload    - автоматическая перезагрузка при изменениях кода (только для разработки)
# --port 7990 - порт для запуска сервера
# --host 0.0.0.0 - доступ со всех интерфейсов
```

### Решение частых проблем при запуске

#### 1. Ошибка "uvicorn не распознано как имя командлета"
**Причина**: Uvicorn не установлен или не доступен в PATH
**Решение**: Используйте альтернативную команду:
```bash
python -m uvicorn app.main:app --reload
```

#### 2. Ошибка "ModuleNotFoundError: No module named 'defusedxml'"
**Причина**: Отсутствуют необходимые зависимости
**Решение**: Установите все зависимости из requirements.txt:
```bash
pip install -r requirements.txt
```

#### 3. Ошибка "Form data requires 'python-multipart' to be installed"
**Причина**: Отсутствует пакет python-multipart
**Решение**: Установите пакет:
```bash
pip install python-multipart==0.0.20
```

#### 4. Ошибка "Cannot use `Query` for path param 'param_name'"
**Причина**: Неправильное объявление параметров пути в FastAPI
**Решение**: Убедитесь, что параметры пути объявлены правильно:
```python
# Правильно:
@router.get("/{model_id}/{param_name}")
async def get_parameter(model_id: str, param_name: str, db: Session = Depends(get_db)):
    ...

# Неправильно (использование Query для path параметра):
@router.get("/{model_id}/{param_name}")
async def get_parameter(model_id: str, param_name: str = Query(...), db: Session = Depends(get_db)):
    ...
```

## Примеры API

### Работа с изображениями товаров

#### Загрузка изображения
```
POST /api/modelgoods/image/
```
Параметры формы:
- `modelid` (обязательный) - ID товара
- `file` (обязательный) - файл изображения

Ответ:
```json
{
  "status": "success",
  "filename": "00000000000001_00000000000002.jpg",
  "message": null
}
```

#### Получение информации об изображении
```
GET /api/modelgoods/image/{modelid}
```
Параметры пути:
- `modelid` - ID товара

Ответ:
```json
{
  "modelid": "00000000000001",
  "filename": "00000000000001_00000000000002.jpg",
  "imgext": "jpg",
  "changedate": "2026-02-12 19:30:45"
}
```

#### Удаление изображения
```
DELETE /api/modelgoods/image/{modelid}
```
Параметры пути:
- `modelid` - ID товара

Ответ:
```json
{
  "status": "success",
  "message": "Image deleted successfully"
}
```

### Другие API
- Получение последних 50 товаров без описаний в файле: `GET /api/products/`
- Проверка здоровья системы: `GET /healthcheck`
- Сохранение параметров товара: `POST /api/modelgoods/parameters/{model_id}`
- Получение параметров товара: `GET /api/modelgoods/parameters/{model_id}`
- Получение инвентаря с фильтром по трейлерам: `GET /` (исключает Folders.istrailer=1)

## Новые функции

### Управление изображениями товаров
- **Полнофункциональный API** для работы с изображениями товаров:
  - Загрузка изображений через `POST /api/modelgoods/image/` (использует подход через временный файл)
  - Получение информации об изображении через `GET /api/modelgoods/image/{modelid}`
  - Удаление изображений через `DELETE /api/modelgoods/image/{modelid}`
- **Интеграция с базой данных**: автоматическое обновление поля `imgext` в таблице `modelgoods`
- **Безопасное хранение**: использование хранимых процедур Firebird для работы с файлами
- **Обработка ошибок**: корректная обработка отсутствующих товаров и файлов
- **Оптимизированный подход**: использование временных файлов для надежной передачи данных в хранимые процедуры

### Технические улучшения
- **Оптимизированный подход к загрузке изображений**: использование временных файлов аналогично сохранению параметров
- **Улучшенная обработка результатов хранимых процедур**: использование `.fetchall()` для надежного получения результатов
- **Полная документация**: созданы файлы `IMAGE_UPLOAD_API.md` и `README_IMAGE_UPLOAD.md` с примерами использования
- **Комплексное тестирование**: добавлены тесты для проверки всех аспектов работы системы

### Улучшения интерфейса
- Добавлен фильтр трейлеров в основном интерфейсе инвентаря
- Реализована пагинация с учетом фильтрации по трейлерам

### Тестирование
- Добавлены тесты для API работы с изображениями (`tests/test_modelgoods_images.py`)
- Проверка структуры API и обработки ошибок

## Исправление ошибки первичного ключа (modelgoods_external_images)

### Проблема
При добавлении внешних изображений возникала ошибка:
```
SQLCODE: -803
violation of PRIMARY or UNIQUE KEY constraint 'PK_modelgoods_external_images'
Problematic key value is ('id' = '0')
```

### Причина
SQLAlchemy передавал значение `id='0'` из-за наличия `server_default=text("'0'")` в определении поля `id` модели `ModelgoodsExternalImages`. Триггер в Firebird ожидал `UID_NULL()` для генерации нового ID через функцию `GetID()`.

### Решение
Удален `server_default=text("'0'")` из поля `id` в модели `ModelgoodsExternalImages`. Теперь SQLAlchemy не передает значение по умолчанию, и триггер в Firebird может корректно сгенерировать новый ID.

### Проверка
1. Модель исправлена - поле `id` больше не имеет `server_default`
2. SQLAlchemy не будет передавать `id='0'` при вставке новых записей
3. Триггер в Firebird сможет сгенерировать новый ID через `GetID()`
4. Ошибка нарушения первичного ключа больше не возникает

## Работа с внешними изображениями

### API для внешних изображений
- **Валидация URL изображения**: `POST /api/modelgoods/external-images/validate`
- **Добавление ссылки на внешнее изображение**: `POST /api/modelgoods/external-images/`
- **Получение всех ссылок для товара**: `GET /api/modelgoods/external-images/{modelid}`
- **Обновление статусов изображения**: `PUT /api/modelgoods/external-images/{image_id}`
- **Удаление ссылки на изображение**: `DELETE /api/modelgoods/external-images/{image_id}`
- **Получение всех ссылок с фильтрами**: `GET /api/modelgoods/external-images/`

### Примеры использования

#### Валидация изображения
```bash
curl -X POST "http://localhost:7990/api/modelgoods/external-images/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/image.jpg"
  }'
```

#### Добавление внешнего изображения
```bash
curl -X POST "http://localhost:7990/api/modelgoods/external-images/" \
  -H "Content-Type: application/json" \
  -d '{
    "modelid": "000001002Qa{",
    "url": "https://cdn.vseinstrumenti.ru/images/goods/.../image.jpg",
    "userid": "0"
  }'
```

#### Получение изображений для товара
```bash
curl "http://localhost:7990/api/modelgoods/external-images/000001002Qa{"
```

## Тестирование
```bash
pytest tests/
