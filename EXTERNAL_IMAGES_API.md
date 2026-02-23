# API для работы с внешними изображениями товаров

## Обзор

API предоставляет функционал для управления ссылками на внешние изображения товаров. Система позволяет:
- Добавлять ссылки на изображения из внешних источников
- Валидировать изображения перед добавлением
- Управлять статусами изображений (одобрение, загрузка в БД)
- Фильтровать и получать изображения по различным критериям

## Технические детали

### Базовая информация
- **Базовый URL**: `/api/modelgoods/external-images`
- **Тип данных**: JSON
- **Аутентификация**: Не требуется (в текущей реализации)
- **Кодировка**: UTF-8

### Структура таблицы
Таблица `modelgoods_external_images` содержит следующие поля:

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | CHAR(12) | Уникальный идентификатор записи | PRIMARY KEY |
| `modelid` | CHAR(12) | ID товара | FOREIGN KEY к `modelgoods.id` |
| `url` | VARCHAR(2000) | URL изображения | NOT NULL |
| `is_approved` | INTEGER | Статус одобрения | 0/1, DEFAULT 0 |
| `is_loaded_to_db` | INTEGER | Статус загрузки в БД | 0/1, DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP | Дата обновления | DEFAULT CURRENT_TIMESTAMP |
| `userid` | CHAR(12) | ID пользователя | DEFAULT '0' |

## Эндпоинты API

### 1. Валидация изображения

**POST** `/api/modelgoods/external-images/validate`

Проверяет валидность изображения по URL перед добавлением.

#### Запрос
```json
{
  "url": "https://example.com/image.jpg"
}
```

#### Ответ
```json
{
  "is_valid": true,
  "message": "Изображение валидно. Размер: 1200x800",
  "details": {
    "width": 1200,
    "height": 800,
    "size": 150000
  }
}
```

#### Проверки
1. Доступность URL (HTTP 200)
2. Content-Type: image/jpeg или image/jpg
3. Минимальный размер: 800x600 пикселей
4. Максимальный размер файла для проверки: 2MB

### 2. Добавление изображения

**POST** `/api/modelgoods/external-images/`

Добавляет ссылку на внешнее изображение для товара.

#### Запрос
```json
{
  "modelid": "000001002Qa{",
  "url": "https://example.com/image.jpg",
  "userid": "0"
}
```

#### Ответ (201 Created)
```json
{
  "id": "001234567890",
  "modelid": "000001002Qa{",
  "url": "https://example.com/image.jpg",
  "userid": "0",
  "is_approved": 0,
  "is_loaded_to_db": 0,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

#### Ограничения
- `modelid` должен существовать в таблице `modelgoods`
- `modelid` должен быть ровно 12 символов
- URL должен проходить валидацию

### 3. Получение изображений по товару

**GET** `/api/modelgoods/external-images/{modelid}`

Получает все изображения для указанного товара.

#### Параметры запроса
| Параметр | Тип | Описание | По умолчанию |
|----------|-----|----------|--------------|
| `is_approved` | integer | Фильтр по статусу одобрения | - |
| `is_loaded_to_db` | integer | Фильтр по статусу загрузки | - |

#### Пример запроса
```
GET /api/modelgoods/external-images/000001002Qa{?is_approved=1&is_loaded_to_db=0
```

#### Ответ
```json
{
  "images": [
    {
      "id": "001234567890",
      "modelid": "000001002Qa{",
      "url": "https://example.com/image.jpg",
      "userid": "0",
      "is_approved": 1,
      "is_loaded_to_db": 0,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1
}
```

### 4. Получение всех изображений

**GET** `/api/modelgoods/external-images/`

Получает все изображения с поддержкой фильтрации и пагинации.

#### Параметры запроса
| Параметр | Тип | Описание | По умолчанию |
|----------|-----|----------|--------------|
| `modelid` | string | Фильтр по ID товара | - |
| `is_approved` | integer | Фильтр по статусу одобрения | - |
| `is_loaded_to_db` | integer | Фильтр по статусу загрузки | - |
| `limit` | integer | Лимит записей | 100 |
| `offset` | integer | Смещение | 0 |

#### Пример запроса
```
GET /api/modelgoods/external-images/?modelid=000001002Qa{&is_approved=1&limit=50&offset=0
```

### 5. Обновление статусов

**PUT** `/api/modelgoods/external-images/{image_id}`

Обновляет статусы изображения.

#### Запрос
```json
{
  "is_approved": 1,
  "is_loaded_to_db": 1
}
```

#### Ответ
```json
{
  "id": "001234567890",
  "status": "success",
  "message": "Статусы успешно обновлены"
}
```

### 6. Удаление изображения

**DELETE** `/api/modelgoods/external-images/{image_id}`

Удаляет ссылку на изображение.

#### Ответ
```json
{
  "id": "001234567890",
  "status": "success",
  "message": "Ссылка на изображение успешно удалена"
}
```

## Коды ошибок

| Код | Описание | Возможные причины |
|-----|----------|-------------------|
| 400 | Bad Request | Невалидные данные, неправильный формат URL |
| 404 | Not Found | Товар или изображение не найдено |
| 500 | Internal Server Error | Ошибка сервера, проблемы с БД |

## Примеры использования

### Пример 1: Полный цикл работы с изображением

```python
import requests

BASE_URL = "http://localhost:7990/api/modelgoods/external-images"

# 1. Валидация изображения
validation_response = requests.post(f"{BASE_URL}/validate", json={
    "url": "https://example.com/product-image.jpg"
})

if validation_response.json()["is_valid"]:
    # 2. Добавление изображения
    create_response = requests.post(f"{BASE_URL}/", json={
        "modelid": "000001002Qa{",
        "url": "https://example.com/product-image.jpg",
        "userid": "0"
    })
    
    image_id = create_response.json()["id"]
    
    # 3. Одобрение изображения
    requests.put(f"{BASE_URL}/{image_id}", json={
        "is_approved": 1
    })
    
    # 4. Получение одобренных изображений
    approved_images = requests.get(f"{BASE_URL}/000001002Qa{", params={
        "is_approved": 1
    })
```

### Пример 2: Массовая обработка изображений

```python
import requests
from concurrent.futures import ThreadPoolExecutor

def process_image(modelid, url):
    """Обработка одного изображения"""
    BASE_URL = "http://localhost:7990/api/modelgoods/external-images"
    
    # Проверка валидности
    validation = requests.post(f"{BASE_URL}/validate", json={"url": url})
    if not validation.json()["is_valid"]:
        return None
    
    # Добавление
    response = requests.post(f"{BASE_URL}/", json={
        "modelid": modelid,
        "url": url,
        "userid": "0"
    })
    
    return response.json()["id"] if response.status_code == 201 else None

# Массовая обработка
images_to_process = [
    ("000001002Qa{", "https://example.com/image1.jpg"),
    ("000001002Qa{", "https://example.com/image2.jpg"),
    ("000001002Qb{", "https://example.com/image3.jpg"),
]

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(lambda x: process_image(*x), images_to_process))
```

## Интеграция с существующей системой

### Связь с таблицей modelgoods
- Внешние изображения связаны с товарами через поле `modelid`
- При удалении товара рекомендуется удалять связанные изображения
- Можно использовать для расширения функционала загрузки изображений

### Статусы изображений
1. **is_approved** (0/1):
   - 0: Изображение добавлено, но не проверено модератором
   - 1: Изображение одобрено для использования

2. **is_loaded_to_db** (0/1):
   - 0: Изображение только в виде ссылки
   - 1: Изображение загружено в локальную БД (через процедуру wp_SaveBlobToFile)

## Рекомендации по использованию

### Безопасность
1. Всегда валидируйте URL перед добавлением
2. Ограничивайте размер загружаемых изображений
3. Используйте HTTPS для передачи данных

### Производительность
1. Используйте пагинацию при получении больших списков
2. Кэшируйте результаты запросов при частом доступе
3. Используйте асинхронные запросы для массовых операций

### Мониторинг
1. Логируйте все операции с изображениями
2. Отслеживайте ошибки валидации
3. Мониторьте использование дискового пространства

## Устранение неполадок

### Частые ошибки

1. **"Товар с ID ... не найден"**
   - Проверьте существование товара в таблице `modelgoods`
   - Убедитесь, что `modelid` имеет ровно 12 символов

2. **"Не удалось загрузить изображение"**
   - Проверьте доступность URL
   - Убедитесь, что сервер отдает изображение с правильным Content-Type
   - Проверьте размер изображения (минимум 400x300)

3. **"Неправильный тип контента"**
   - Поддерживаются только JPG/JPEG изображения
   - Проверьте расширение файла и Content-Type

### Логирование
Все операции логируются с использованием logger.getLogger("api"). Уровни логирования:
- DEBUG: Детальная информация о параметрах
- INFO: Успешные операции
- WARNING: Предупреждения (например, невалидные URL)
- ERROR: Ошибки при работе с БД

## Дополнительные возможности

### Автоматическая миграция
При запуске приложения автоматически проверяется существование таблицы `modelgoods_external_images`. Если таблица не существует, она создается автоматически.

### Расширение функционала
API можно расширить для поддержки:
- Пакетной загрузки изображений
- Автоматической загрузки изображений в БД
- Интеграции с системами модерации
- Статистики использования изображений