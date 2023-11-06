import os
import re

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


class PhoneFormatter:
    """Класс отвечающий за форматирование телефона"""

    @staticmethod
    def get_phone(phone):
        """Форматируем номер телефона"""

        if not phone:
            return "+7 (666) 666-66-66"

        digits = re.sub(r'\D', '', phone)

        # Проверяем начало номера и длину
        if len(digits) == 11 and (digits.startswith('7') or digits.startswith('8')):
            # Используем срез для форматирования, отбрасывая первую цифру
            return "+7 ({}) {}-{}-{}".format(digits[1:4], digits[4:7], digits[7:9], digits[9:11])
        elif len(digits) == 10:
            # Если номер уже без ведущей 7 или 8
            return "+7 ({}) {}-{}-{}".format(digits[0:3], digits[3:6], digits[6:8], digits[8:10])
        elif phone == 'yes':
            return "+7 (666) 666-66-66"
        else:
            return phone