# Dockerfile
FROM python:3.10-slim

# Установите зависимости для psycopg2 (если вы перейдете на PostgreSQL позже)
# RUN apt-get update && apt-get install -y \
#     libpq-dev \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

# Установите зависимости для других потенциальных пакетов
RUN apt-get update && apt-get install -y \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Скопируйте файл зависимостей первым, чтобы использовать кэш Docker
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Скопируйте весь проект
COPY . .

# По умолчанию команда будет переопределена в docker-compose
# Эта команда используется, если контейнер запускается напрямую через `docker run`
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]