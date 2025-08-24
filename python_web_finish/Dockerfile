# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Открываем порт
EXPOSE 8000

# Создаем volume для базы данных
VOLUME ["/app/data"]

# Команда для запуска приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]