# API загрузки изображений для товаров

Документация по использованию API для загрузки, получения и удаления изображений товаров.

## Базовый URL

```
http://localhost:8000/api/modelgoods/image
```

## 1. Загрузка изображения

### Endpoint
```
POST /api/modelgoods/image/
```

### Параметры
- `modelid` (form-data) - ID товара в базе данных
- `file` (form-data) - файл изображения

### Примеры использования curl

#### Пример 1: Загрузка JPEG изображения
```bash
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@image.jpg"
```

#### Пример 2: Загрузка PNG изображения
```bash
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@product.png"
```

#### Пример 3: Загрузка GIF изображения
```bash
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@animation.gif"
```

#### Пример 4: Загрузка с указанием полного пути к файлу
```bash
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@C:\Users\username\Pictures\product.jpg"
```

#### Пример 5: Загрузка с выводом подробной информации
```bash
curl -v -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@image.jpg"
```

### Успешный ответ
```json
{
  "status": "success",
  "filename": "1_633150.jpg"
}
```

### Ошибки
- `404 Not Found` - товар с указанным ID не найден
- `500 Internal Server Error` - ошибка при сохранении файла

## 2. Получение информации об изображении

### Endpoint
```
GET /api/modelgoods/image/{modelid}
```

### Примеры использования curl

#### Пример 1: Получение информации об изображении
```bash
curl "http://localhost:8000/api/modelgoods/image/000001002Qa{"
```

#### Пример 2: Получение информации с форматированным выводом
```bash
curl "http://localhost:8000/api/modelgoods/image/000001002Qa{" | python -m json.tool
```

### Успешный ответ
```json
{
  "modelid": "000001002Qa{",
  "filename": "1_633150.jpg",
  "imgext": "jpg",
  "changedate": "2026-02-20 19:31:31.987000"
}
```

### Ошибки
- `404 Not Found` - товар не найден или у товара нет изображения

## 3. Удаление изображения

### Endpoint
```
DELETE /api/modelgoods/image/{modelid}
```

### Примеры использования curl

#### Пример 1: Удаление изображения
```bash
curl -X DELETE "http://localhost:8000/api/modelgoods/image/000001002Qa{"
```

#### Пример 2: Удаление с выводом подробной информации
```bash
curl -v -X DELETE "http://localhost:8000/api/modelgoods/image/000001002Qa{"
```

### Успешный ответ
```json
{
  "status": "success",
  "message": "Image deleted successfully"
}
```

### Ответ с предупреждением (если файл не удалось удалить)
```json
{
  "status": "warning",
  "message": "File delete failed but record cleared: [описание ошибки]"
}
```

## 4. Пакетные операции

### Пример 1: Загрузка нескольких изображений
```bash
# Загрузка первого изображения
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@image1.jpg"

# Загрузка второго изображения (перезапись)
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@image2.png"
```

### Пример 2: Полный цикл работы с изображением
```bash
# 1. Загрузка изображения
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@product.jpg"

# 2. Проверка загруженного изображения
curl "http://localhost:8000/api/modelgoods/image/000001002Qa{"

# 3. Удаление изображения
curl -X DELETE "http://localhost:8000/api/modelgoods/image/000001002Qa{"

# 4. Проверка, что изображение удалено
curl "http://localhost:8000/api/modelgoods/image/000001002Qa{"
```

## 5. Скрипты для автоматизации

### Скрипт для Windows (upload_image.bat)
```batch
@echo off
set MODEL_ID=000001002Qa{
set IMAGE_FILE=product.jpg
set API_URL=http://localhost:8000/api/modelgoods/image/

echo Загрузка изображения %IMAGE_FILE% для товара %MODEL_ID%
curl -X POST "%API_URL%" -F "modelid=%MODEL_ID%" -F "file=@%IMAGE_FILE%"
pause
```

### Скрипт для Linux/macOS (upload_image.sh)
```bash
#!/bin/bash
MODEL_ID="000001002Qa{"
IMAGE_FILE="product.jpg"
API_URL="http://localhost:8000/api/modelgoods/image/"

echo "Загрузка изображения $IMAGE_FILE для товара $MODEL_ID"
curl -X POST "$API_URL" -F "modelid=$MODEL_ID" -F "file=@$IMAGE_FILE"
```

## 6. Особенности работы

### Имя файла
- Имя файла формируется автоматически на основе ID товара
- Формат: `{part0}_{part1}.{расширение}`
- Пример: `1_633150.jpg`

### Расширение файла
- Расширение определяется из имени загружаемого файла
- Поддерживаются: jpg, jpeg, png, gif, bmp, webp
- Регистр не имеет значения

### Хранение файлов
- Файлы сохраняются в каталоге: `C:\Program Files (x86)\tdt3\bases\img\`
- Путь можно изменить через переменные окружения:
  - `BASE_DIR` - базовый каталог
  - `IMG_SUBDIR` - подкаталог для изображений

### Логирование
- Все операции логируются с уровнем DEBUG
- В логах можно увидеть:
  - Параметры хранимой процедуры
  - Размер загружаемого файла
  - Результат выполнения операций
  - Ошибки (если возникают)

## 7. Переменные окружения

```bash
# Базовый каталог для хранения файлов
BASE_DIR=C:\Program Files (x86)\tdt3\bases

# Подкаталог для изображений
IMG_SUBDIR=img

# Уровень логирования (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=DEBUG
```

## 8. Тестирование API

### Тестовые команды curl

```bash
# Тест 1: Загрузка тестового изображения
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@test_image.jpg"

# Тест 2: Проверка загруженного изображения
curl "http://localhost:8000/api/modelgoods/image/000001002Qa{"

# Тест 3: Удаление тестового изображения
curl -X DELETE "http://localhost:8000/api/modelgoods/image/000001002Qa{"

# Тест 4: Проверка после удаления (должна быть ошибка 404)
curl "http://localhost:8000/api/modelgoods/image/000001002Qa{"
```

## 9. Примеры ответов

### Успешная загрузка
```json
{
  "status": "success",
  "filename": "1_633150.jpg"
}
```

### Товар не найден
```json
{
  "detail": "Model not found"
}
```

### Ошибка сохранения файла
```json
{
  "detail": "File save failed: [описание ошибки]"
}
```

### Изображение не найдено
```json
{
  "detail": "Image not found for this model"
}
```

## 10. Советы по использованию

1. **Проверяйте ID товара** перед загрузкой изображения
2. **Используйте правильные расширения** файлов
3. **Мониторьте логи** при возникновении проблем
4. **Тестируйте API** перед использованием в production
5. **Обрабатывайте ошибки** в клиентских приложениях

## 11. Поддержка

При возникновении проблем:
1. Проверьте логи приложения
2. Убедитесь, что товар существует в БД
3. Проверьте права доступа к каталогу изображений
4. Убедитесь, что служба Firebird запущена
5. Проверьте соединение с базой данных