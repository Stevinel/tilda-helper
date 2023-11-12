import os
import re

import requests
from sentry_sdk import capture_message

API_NAME = os.getenv("API_NAME")
API_KEY = os.getenv("API_KEY")
TG_BOT_URL = "http://tgbot:5555"


class MessageSender:
    """Класс отвечающий за рассылку в контейнер с тг ботом"""

    def send_success_message(self, message: str):
        """Отправка успешных сообщений в тг"""

        tg_data = {API_NAME: API_KEY, "message": message}
        response = requests.post(f"{TG_BOT_URL}/notification/send_message/", json=tg_data)

        if response.status_code != 200:
            return capture_message("Не удалось отправить сообщение в телеграм")

    def send_error_message(self, message: str):
        """Отправка сообщений об ошибке в тг"""

        tg_data = {API_NAME: API_KEY, "message": message}
        response = requests.post(f"{TG_BOT_URL}/notification/send_error/", json=tg_data)

        if response.status_code != 200:
            return capture_message("Не удалось отправить сообщение об ошибке в телеграм")


class Formatter:
    """Класс отвечающий за форматирование входящих данных"""

    @staticmethod
    def format_phone(phone: str) -> str:
        """Приведение номера телефона к нужному формату"""

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

    @staticmethod
    def format_email(email: str) -> str:
        """Приведение почты к нужному формату"""

        if email.endswith("gmail.ru"):
            email = email.replace("gmail.ru", "gmail.com")
        return email

    @staticmethod
    def format_full_name(name: str) -> tuple:
        """Приведение имени к нужному формату"""

        full_name = name.split()

        last_name = full_name[0] if len(full_name) >= 1 else ""
        first_name = full_name[1] if len(full_name) >= 2 else ""
        patronymic_name = full_name[2] if len(full_name) == 3 else ""
        return last_name, first_name, patronymic_name

    @staticmethod
    def format_payment(payment: str) -> int:
        """Приведение суммы платежа к нужному формату"""

        if isinstance(payment, dict):
            payment_amount = payment["payment"]["amount"].replace(',', '.')
        else:
            payment_amount = payment.replace(',', '.')
        return int(float(payment_amount))

    @staticmethod
    def create_customer_dict(
            first_name: str | None,
            last_name: str | None,
            patronymic_name: str | None,
            email: str | None,
            phone_number: str | None
    ) -> dict:
        """Формирование словаря с данными клиента"""

        return {
            "customer": {
                "first_name": first_name,
                "last_name": last_name,
                "patronymic_name": patronymic_name,
                "email": email,
                "phone_number": phone_number,
            }
        }

    @staticmethod
    def create_order_dict(order_number: str, payment_amount: int) -> dict:
        """Формирование словаря с данными заказа"""

        return {
            "order": {
                "order_number": order_number,
                "payment_amount": payment_amount,
            }
        }

    @staticmethod
    def create_products_dict(products_data: dict | list, default_quantity=1) -> dict:
        """Формирование словаря с данными товаров"""

        products = {"products": []}
        for product_data in products_data:
            if isinstance(product_data, dict):
                product = {
                    "article": product_data["sku"],
                    "quantity": product_data.get("quantity", default_quantity),
                }
            else:
                product = {
                    "article": product_data,
                    "quantity": default_quantity,
                }
            products["products"].append(product)
        return products
