#!/bin/bash
# Скрипт для автоматического запуска всех тестов
# Использование: ./run_tests.sh [опции]

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия pytest
check_pytest() {
    if ! python -m pytest --version > /dev/null 2>&1; then
        print_error "pytest не найден. Установите: pip install pytest"
        exit 1
    fi
    print_success "pytest найден"
}

# Запуск всех тестов
run_all_tests() {
    print_info "Запуск всех тестов..."
    python -m pytest tests/ -v --tb=short
    return $?
}

# Запуск тестов по паттерну
run_tests_by_pattern() {
    local pattern=$1
    print_info "Запуск тестов с паттерном: $pattern"
    python -m pytest tests/ -v --tb=short -k "$pattern"
    return $?
}

# Запуск тестов из конкретного файла
run_tests_from_file() {
    local file=$1
    print_info "Запуск тестов из файла: $file"
    python -m pytest "$file" -v --tb=short
    return $?
}

# Основная функция
main() {
    echo "========================================"
    echo "🚀 АВТОМАТИЧЕСКИЙ ЗАПУСК ТЕСТОВ"
    echo "========================================"
    
    # Проверка pytest
    check_pytest
    
    # Обработка аргументов
    case "$1" in
        --pattern|-k)
            if [ -z "$2" ]; then
                print_error "Не указан паттерн для тестов"
                exit 1
            fi
            run_tests_by_pattern "$2"
            ;;
        --file|-f)
            if [ -z "$2" ]; then
                print_error "Не указан файл с тестами"
                exit 1
            fi
            run_tests_from_file "$2"
            ;;
        --help|-h)
            echo "Использование: $0 [опции]"
            echo ""
            echo "Опции:"
            echo "  --pattern, -k PATTERN  Запустить тесты с указанным паттерном"
            echo "  --file, -f FILE        Запустить тесты из указанного файла"
            echo "  --help, -h             Показать эту справку"
            echo ""
            echo "Примеры:"
            echo "  $0                     Запустить все тесты"
            echo "  $0 -k \"modelid\"       Запустить тесты с паттерном 'modelid'"
            echo "  $0 -f tests/test_main.py  Запустить тесты из файла"
            exit 0
            ;;
        *)
            # Запуск всех тестов по умолчанию
            run_all_tests
            ;;
    esac
    
    # Проверка результата
    if [ $? -eq 0 ]; then
        echo ""
        print_success "Все тесты прошли успешно!"
        exit 0
    else
        echo ""
        print_error "Тесты не прошли!"
        exit 1
    fi
}

# Запуск основной функции
main "$@"