# Backend Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Копирование всего проекта
COPY . .

# Копирование requirements
RUN pip install --no-cache-dir -e ./backend

# Expose порт
EXPOSE 5030

# Запуск приложения
WORKDIR /app/backend
CMD ["uvicorn", "main:create_app", "--host", "0.0.0.0", "--port", "5030"]