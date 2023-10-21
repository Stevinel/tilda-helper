import os
from functools import wraps

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

import telebot
from apps.webhook.manager import DataManager
from django.conf import settings
from django.http import JsonResponse
from sentry_sdk import capture_exception

from .serializers import TgSerializer

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")
ALLOWED_CHATS = [x.strip() for x in os.getenv("ALLOWED_CHATS").split(",")]

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def access_verification(view_func):
    """Декоратор проверки доступа к боту"""

    @wraps(view_func)
    def _wrapped_view(data):
        if not str(data.chat.id) in ALLOWED_CHATS:
            return

        return view_func(data)

    return _wrapped_view


def get_container_data(client):
    """Получение состояния контейнеров"""

    container_names = {
        'name': [
            'tgbot',
            'celery',
            'nginx',
            'backend',
            'postgres',
            'redis',
            'backup',
        ]
    }
    containers = client.containers.list(filters=container_names)
    container_data = []
    for container in containers:
        container_info = {
            "name": container.name,
            "status": container.status,
        }
        container_data.append(container_info)

    return container_data


def wake_up_msg():
    """Отправка приветствующего сообщения"""

    bot.send_message(TARGET_CHAT_ID, "Я запустился")


@bot.message_handler(commands=['status'])
@access_verification
def get_containers_status(message):
    """Проверка статусов контейнеров"""

    if not settings.DEBUG:
        import docker
        client = docker.from_env()
    else:
        return bot.reply_to(message, "Выключите debug режим")

    container_statuses = get_container_data(client)
    msg = ''
    if container_statuses:
        for container in container_statuses:
            msg += f"Контейнер: {container['name']} - {container['status']}\n"
    if msg:
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "Не удалось получить статусы контейнеров")


@bot.message_handler(func=lambda message: True)
@access_verification
def get_order_data(message):
    """Получение заказа в тг бота, для отправки в ручном режиме"""

    serializer = TgSerializer()
    try:
        customer, order, products = serializer.serialize(message)
    except Exception as e:
        capture_exception(e)
        bot.reply_to(message, "Ошибка данных")
        return JsonResponse({"error": "Data serialization error"})

    manager = DataManager(customer, order, products)
    manager.save_data()
    bot.reply_to(message, "Заказ принят")


if __name__ == "__main__":
    if not settings.DEBUG:
        wake_up_msg()

    bot.infinity_polling()
