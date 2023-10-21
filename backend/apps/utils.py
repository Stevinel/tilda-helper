import os

import requests
from sentry_sdk import capture_message

API_NAME = os.getenv("API_NAME")
API_KEY = os.getenv("API_KEY")
TG_BOT_URL = "http://tgbot:5555"


class MessageSender:
    """Класс отвечающий за рассылку в контейнер с тг ботом"""

    def send_success_message(self, message):
        """Отправка успешных сообщений в тг"""

        tg_data = {API_NAME: API_KEY, "message": message}
        response = requests.post(f"{TG_BOT_URL}/notification/send_message/", json=tg_data)

        if response.status_code != 200:
            return capture_message("Не удалось отправить сообщение в телеграм")

    def send_error_message(self, message):
        """Отправка сообщений об ошибке в тг"""

        tg_data = {API_NAME: API_KEY, "message": message}
        response = requests.post(f"{TG_BOT_URL}/notification/send_error/", json=tg_data)

        if response.status_code != 200:
            return capture_message("Не удалось отправить сообщение об ошибке в телеграм")
