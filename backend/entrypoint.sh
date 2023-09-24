#!/bin/bash
python manage.py migrate --no-input
python manage.py collectstatic --no-input
gunicorn config.wsgi:application -b 0.0.0.0:8000 --reload & celery -A config worker
python apps/telegram_bot/main.py