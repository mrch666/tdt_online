# Загрузка изображений для товаров

## Краткое руководство по API

### Быстрый старт

1. **Запустите сервер**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Загрузите изображение**:
```bash
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@product.jpg"
```

3. **Проверьте загруженное изображение**:
```bash
curl "http://localhost:8000/api/modelgoods/image/000001002Qa{"
```

### Основные команды curl

#### Загрузка изображения
```bash
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=<ID_товара>" \
  -F "file=@<путь_к_файлу>"
```

#### Получение информации
```bash
curl "http://localhost:8000/api/modelgoods/image/<ID_товара>"
```

#### Удаление изображения
```bash
curl -X DELETE "http://localhost:8000/api/modelgoods/image/<ID_товара>"
```

### Примеры для разных типов файлов

```bash
# JPEG
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@image.jpg"

# PNG  
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@image.png"

# GIF
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@image.gif"
```

### Скрипт для автоматической загрузки (Windows)

Создайте файл `upload.bat`:
```batch
@echo off
set MODEL_ID=000001002Qa{
set IMAGE_FILE=%1
set API_URL=http://localhost:8000/api/modelgoods/image/

if "%IMAGE_FILE%"=="" (
    echo Использование: upload.bat <путь_к_файлу>
    exit /b 1
)

echo Загрузка %IMAGE_FILE% для товара %MODEL_ID%
curl -X POST "%API_URL%" -F "modelid=%MODEL_ID%" -F "file=@%IMAGE_FILE%"
```

Использование:
```bash
upload.bat C:\Images\product.jpg
```

### Скрипт для автоматической загрузки (Linux/macOS)

Создайте файл `upload.sh`:
```bash
#!/bin/bash
MODEL_ID="000001002Qa{"
IMAGE_FILE="$1"
API_URL="http://localhost:8000/api/modelgoods/image/"

if [ -z "$IMAGE_FILE" ]; then
    echo "Использование: $0 <путь_к_файлу>"
    exit 1
fi

echo "Загрузка $IMAGE_FILE для товара $MODEL_ID"
curl -X POST "$API_URL" -F "modelid=$MODEL_ID" -F "file=@$IMAGE_FILE"
```

Сделайте скрипт исполняемым и используйте:
```bash
chmod +x upload.sh
./upload.sh /path/to/product.jpg
```

### Тестовые данные

Для тестирования используйте товар с ID: `000001002Qa{`

Этот товар:
- Существует в базе данных
- Имеет числовые части ID: 1 и 633150
- Будет создавать файлы с именами: `1_633150.<расширение>`

### Проверка работы

1. **Проверьте, что сервер запущен**:
```bash
curl "http://localhost:8000/"
```

2. **Проверьте API изображений**:
```bash
curl "http://localhost:8000/api/modelgoods/image/000001002Qa{"
```

3. **Загрузите тестовое изображение**:
```bash
# Создайте тестовый файл
echo "test" > test.jpg

# Загрузите его
curl -X POST "http://localhost:8000/api/modelgoods/image/" \
  -F "modelid=000001002Qa{" \
  -F "file=@test.jpg"
```

### Переменные окружения

```bash
# Для Windows
set BASE_DIR=C:\Program Files (x86)\tdt3\bases
set IMG_SUBDIR=img

# Для Linux/macOS
export BASE_DIR=/opt/tdt3/bases
export IMG_SUBDIR=img
```

### Логирование

Для просмотра логов:
- Запустите сервер в терминале
- Или проверьте файлы логов
- Уровень логирования: DEBUG (показывает все детали)

### Устранение неполадок

1. **"Model not found"** - проверьте ID товара
2. **"File save failed"** - проверьте права доступа к каталогу
3. **Нет ответа от сервера** - проверьте, что сервер запущен
4. **Файл не появляется** - проверьте каталог `C:\Program Files (x86)\tdt3\bases\img\`

### Полная документация

Подробная документация с примерами: [IMAGE_UPLOAD_API.md](IMAGE_UPLOAD_API.md)

### Контакты

При возникновении проблем:
1. Проверьте логи сервера
2. Убедитесь, что база данных доступна
3. Проверьте права доступа к файловой системе
4. Обратитесь к разработчикам системы