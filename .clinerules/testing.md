# Правила тестирования для проекта FastAPI

## Общие принципы
1. **Тестирование перед изменением** - всегда создавать тесты перед внесением изменений
2. **Изоляция тестов** - каждый тест должен быть независимым
3. **Воспроизводимость** - тесты должны давать одинаковые результаты при каждом запуске

## Типы тестов
### 1. Unit-тесты
- Тестирование отдельных функций и методов
- Мокирование внешних зависимостей
- Быстрое выполнение

### 2. Интеграционные тесты
- Тестирование взаимодействия с базой данных
- Проверка хранимых процедур
- Тестирование API endpoints

### 3. Функциональные тесты
- Тестирование полного потока работы
- Проверка бизнес-логики
- Тестирование с реальными данными

## Структура тестов
```
tests/
├── unit/
│   ├── test_models.py
│   └── test_utils.py
├── integration/
│   ├── test_database.py
│   └── test_procedures.py
└── functional/
    ├── test_api.py
    └── test_workflows.py
```

## Правила написания тестов
### Для тестирования параметров
```python
def test_modelid_length():
    """Тест проверки длины modelid (должен быть 12 символов)"""
    # Правильный modelid
    correct_modelid = "000001002Qa{"
    assert len(correct_modelid) == 12
    
    # Тест с неправильной длиной
    with pytest.raises(ValueError):
        process_modelid("1234567890123")  # 13 символов
```

### Для тестирования хранимых процедур
```python
def test_wp_saveblobtofile():
    """Тест вызова хранимой процедуры wp_SaveBlobToFile"""
    # Подготовка тестовых данных
    test_data = {
        'iPathDB': 'C:\\Program Files (x86)\\tdt3\\bases\\img',
        'iPath': 'test_file.jpg',
        'iBlob': b'test content'
    }
    
    # Вызов процедуры
    result = call_procedure('wp_SaveBlobToFile', test_data)
    
    # Проверки
    assert result is not None
    assert os.path.exists(os.path.join(test_data['iPathDB'], test_data['iPath']))
```

### Для тестирования API
```python
def test_image_upload():
    """Тест загрузки изображения через API"""
    # Подготовка тестового файла
    test_file = ('test.jpg', b'test image content', 'image/jpeg')
    
    # Отправка запроса
    response = client.post(
        '/api/modelgoods/image/',
        data={'modelid': '000001002Qa{'},
        files={'file': test_file}
    )
    
    # Проверки
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
```

## Логирование в тестах
- Добавлять логирование параметров при отладке
- Логировать ошибки с деталями
- Использовать разные уровни логирования для разных типов тестов

## Запуск тестов
```bash
# Запуск всех тестов
python -m pytest tests/

# Запуск с детальным выводом
python -m pytest -v tests/

# Запуск конкретного теста
python -m pytest tests/test_modelid_length.py

# Запуск с покрытием кода
python -m pytest --cov=app tests/
```

## Best Practices
1. **Именование тестов** - использовать описательные имена
2. **Очистка после тестов** - удалять созданные файлы и данные
3. **Документация тестов** - добавлять docstrings с описанием теста
4. **Параметризация** - использовать @pytest.mark.parametrize для множества тестовых случаев