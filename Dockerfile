# Лёгкий и стабильный образ на базе Debian Slim
FROM python:3.12-slim

# Устанавливаем системные зависимости (для сборки пакетов Python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip и ставим колёсики быстрее
RUN pip install --upgrade pip setuptools wheel

# Рабочая директория
WORKDIR /app

# Копируем requirements.txt (чтобы слои кэшировались)
COPY requirements.txt .

# Устанавливаем Python-зависимости с увеличенным таймаутом и зеркалом PyPI
RUN pip install --no-cache-dir \
    --default-timeout=200 \
    --retries=10 \
    -i https://mirror.yandex.ru/pypi/simple/ \
    -r requirements.txt

# Копируем весь проект
COPY . .

# Даем права на выполнение скриптов
RUN chmod a+x docker/*.sh

