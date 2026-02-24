#!/usr/bin/env python
"""
Скрипт для запуска сервера FastAPI на свободном порту
"""
import socket
import subprocess
import sys
import os

def find_free_port(start_port=7990, max_attempts=10):
    """Найти свободный порт"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def main():
    # Находим свободный порт
    free_port = find_free_port()
    if not free_port:
        print("Не удалось найти свободный порт")
        sys.exit(1)
    
    print(f"Запуск сервера на порту: {free_port}")
    
    # Устанавливаем переменную окружения для порта
    os.environ['SERVER_PORT'] = str(free_port)
    
    # Команда для запуска сервера
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--reload",
        "--port", str(free_port),
        "--host", "0.0.0.0"
    ]
    
    print(f"Команда: {' '.join(cmd)}")
    
    # Запускаем сервер
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nСервер остановлен")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка запуска сервера: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()