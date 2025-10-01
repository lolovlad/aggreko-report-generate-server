# Используем официальный легковесный образ Python 3.11 на базе Alpine
FROM python:3.12.1-alpine

# Устанавливаем системные зависимости (необходимы для некоторых пакетов)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    libxml2-dev \
    libxslt-dev \
    && pip install --upgrade pip

# Создаём и переходим в рабочую директорию
WORKDIR /app

# Копируем requirements.txt отдельно для кэширования слоёв
COPY requirements.txt .

# Устанавливаем зависимости с увеличенным таймаутом и российским зеркалом PyPI
RUN pip install --no-cache-dir \
    --default-timeout=100 \
    --index-url=https://pypi.mirrors.usto.co/simple/ \
    -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Возвращаем обязательную строку: даём права на выполнение всем скриптам в /docker/
RUN chmod a+x docker/*.sh
