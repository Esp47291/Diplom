FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Миграции при старте задаются в docker-compose (там же volume .:/app перезаписывает файлы с Windows)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
