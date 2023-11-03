import os
from functools import wraps

import django
from celery import shared_task

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

import docker
import telebot
from apps.webhook.manager import DataManager
from django.conf import settings
from django.http import JsonResponse
from sentry_sdk import capture_exception

from .serializers import TgSerializer

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")
ALLOWED_CHATS = [x.strip() for x in os.getenv("ALLOWED_CHATS").split(",")]

BOT = telebot.TeleBot(TELEGRAM_TOKEN)
CONTAINERS = {
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


def access_verification(view_func):
    """Декоратор проверки доступа к боту"""

    @wraps(view_func)
    def _wrapped_view(data):
        if not str(data.chat.id) in ALLOWED_CHATS:
            return

        return view_func(data)

    return _wrapped_view


def get_container_data():
    """Получение состояния контейнеров"""

    docker_client = docker.from_env()
    containers = docker_client.containers.list(filters=CONTAINERS)
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

    BOT.send_message(TARGET_CHAT_ID, "Я запустился")


@BOT.message_handler(commands=['status'])
@access_verification
def get_containers_status(message):
    """Проверка статусов контейнеров"""

    container_statuses = get_container_data()
    msg = ''

    if container_statuses:
        for container in container_statuses:
            msg += f"Контейнер: {container['name']} - {container['status']}\n"
    if msg:
        msg += f"\n Запущено {len(container_statuses)} из 7"
        BOT.reply_to(message, msg)
    else:
        BOT.reply_to(message, "Не удалось получить статусы контейнеров")


@BOT.message_handler(commands=['restart'])
@access_verification
def restart_containers(message):
    """Рестарт контейнеров"""

    docker_client = docker.from_env()
    containers = docker_client.containers.list(filters=CONTAINERS)
    # Move tgbot container to the end
    [containers.append(containers.pop(containers.index(c))) for c in containers if c.name == 'tgbot']

    try:
        for container in containers:
            BOT.reply_to(message, f"Рестарт контейнера {container.name}")
            container.restart()
    except Exception as e:
        BOT.reply_to(message, f"Не удалось перезапустить контейнеры. \n Ошибка: {e}")


@BOT.message_handler(func=lambda message: True)
@access_verification
def get_order_data(message):
    """Получение заказа в тг бота, для отправки в ручном режиме"""

    if not message.text.startswith("Order"):
        return BOT.reply_to(message, "Пришлите заказ или команду")

    serializer = TgSerializer()
    try:
        customer, order, products = serializer.serialize(message)
    except Exception as e:
        capture_exception(e)
        BOT.reply_to(message, "Ошибка данных")
        return JsonResponse({"error": "Data serialization error"})

    manager = DataManager(customer, order, products)
    manager.save_data()
    BOT.reply_to(message, "Заказ принят")


if __name__ == "__main__":
    if not settings.DEBUG:
        wake_up_msg()

    BOT.remove_webhook()
    BOT.set_webhook(
        url=f'{os.getenv("DNS")}/webhook/',
        secret_token=os.getenv("TG_HEADER_TOKEN"),
        max_connections=5
    )