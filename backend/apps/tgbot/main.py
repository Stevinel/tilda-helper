import os

from functools import wraps

import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

import docker
import telebot

from sentry_sdk import capture_exception

from .serializers import TgSerializer

from apps.orders.manager import DataManager

from django.conf import settings
from django.http import JsonResponse


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TARGET_CHAT_ID = os.getenv('TARGET_CHAT_ID')
ALLOWED_CHATS = [x.strip() for x in os.getenv('ALLOWED_CHATS').split(',')]

BOT = telebot.TeleBot(TELEGRAM_TOKEN)
CONTAINERS = {
    'name': [
        'tgbot',
        'celery_send_mails',
        'celery_send_many_mails',
        'nginx',
        'backend',
        'postgres',
        'redis',
        'backup',
        'flower',
    ]
}


def access_verification(view_func):
    """Декоратор проверки доступа к боту"""

    @wraps(view_func)
    def _wrapped_view(data):
        if str(data.chat.id) not in ALLOWED_CHATS:
            return

        return view_func(data)

    return _wrapped_view


def get_container_data() -> list:
    """Получение состояния контейнеров"""

    docker_client = docker.from_env()
    containers = docker_client.containers.list(filters=CONTAINERS)
    container_data = []

    for container in containers:
        container_info = {
            'name': container.name,
            'status': container.status,
        }
        container_data.append(container_info)

    return container_data


def wake_up_msg() -> None:
    """Отправка приветствующего сообщения"""

    BOT.send_message(TARGET_CHAT_ID, 'Бот перезапущен')


@BOT.message_handler(commands=['status'])
@access_verification
def get_containers_status(message: telebot.types.Message) -> telebot.types.Message:
    """Проверка статусов контейнеров"""

    container_statuses = get_container_data()
    msg = ''

    if container_statuses:
        for container in container_statuses:
            msg += f"Контейнер: {container['name']} - {container['status']}\n"
    if msg:
        msg += f'\n Запущено {len(container_statuses)} из 8'
        BOT.reply_to(message, msg)
    else:
        BOT.reply_to(message, 'Не удалось получить статусы контейнеров')


@BOT.message_handler(commands=['restart'])
@access_verification
def restart_containers(message: telebot.types.Message) -> telebot.types.Message:
    """Рестарт контейнеров"""

    docker_client = docker.from_env()
    containers = docker_client.containers.list(filters=CONTAINERS)
    containers = [c for c in containers if c.name != 'tgbot']

    try:
        for container in containers:
            BOT.reply_to(message, f'Рестарт контейнера {container.name}')
            container.restart()
    except Exception as e:
        BOT.reply_to(message, f'Не удалось перезапустить контейнеры. \n Ошибка: {e}')


@BOT.message_handler(func=lambda message: True)
@access_verification
def get_order_data(message: telebot.types.Message) -> JsonResponse | telebot.types.Message:
    """Получение заказа в тг бота, для отправки в ручном режиме"""

    if not message.text.startswith('Order'):
        return BOT.reply_to(message, 'Пришлите заказ или команду')

    serializer = TgSerializer()
    try:
        customer, order, products = serializer.serialize(message)
    except Exception as e:
        capture_exception(e)
        BOT.reply_to(message, f'Ошибка данных {e}')
        return JsonResponse({'error': 'Data serialization error'})

    manager = DataManager(customer, order, products)
    manager.save_data()
    BOT.reply_to(message, 'Заказ принят')


if __name__ == '__main__':
    if not settings.DEBUG:
        wake_up_msg()

    BOT.infinity_polling(long_polling_timeout=30)
