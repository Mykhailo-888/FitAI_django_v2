FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 👉 ВАЖЛИВО: тепер беремо тільки прод requirements
COPY requirements-prod.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "fitai.wsgi:application", "--bind", "0.0.0.0:8000"]