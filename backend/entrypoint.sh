#!/bin/bash
python manage.py migrate --no-input
python manage.py collectstatic --no-input
python apps/telegram_bot/main.py
exec gunicorn config.wsgi:application -b 0.0.0.0:8000 --reload
