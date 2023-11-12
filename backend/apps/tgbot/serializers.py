import re

import telebot

from apps.utils import Formatter


class TgSerializer(Formatter):
    """Сериализация данных, полученных из ТГ"""

    # Методы для поиска данных
    def search_payment_amount(self, text: str) -> int | None:
        """Поиск суммы платежа в тексте"""

        payment_match = re.search(r'Payment Amount: (\d+(\.\d+)?) RUB', text)
        return self.format_payment(payment_match.group(1)) if payment_match else None

    @staticmethod
    def search_articles(text: str) -> list:
        """Поиск артикулов в тексте"""

        article_matches = re.findall(r'\d{6},', text)  # only 6 numbers article
        return [article.rstrip(',') for article in article_matches]

    def search_full_name(self, text: str) -> tuple:
        """Поиск фио в тексте"""

        name_match = re.search(r'Name: (.+)', text)
        return self.format_full_name(name_match.group(1)) if name_match else (None, None, None)

    def search_email(self, text: str) -> str | None:
        """Поиск почты в тексте"""

        email_match = re.search(r'Email: (.+)', text)
        return self.format_email(email_match.group(1)) if email_match else None

    def search_phone(self, text: str) -> str | None:
        """Поиск телефона в тексте"""

        phone_match = re.search(r'Phone: (.+)', text)
        return self.format_phone(phone_match.group(1)) if phone_match else None

    def serialize(self, message: telebot.types.Message) -> tuple:
        """Сериализация входящих данных из ТГ"""

        text = message.text

        # Поиск номера заказа
        order_match = re.search(r'Order #(\d+)', text)
        if not order_match:
            return

        order_number = order_match.group(1)
        payment_amount = self.search_payment_amount(text)
        articles = self.search_articles(text)
        first_name, last_name, patronymic_name = self.search_full_name(text)
        email = self.search_email(text)
        phone_number = self.search_phone(text)

        order_dict = self.create_order_dict(order_number, payment_amount)
        products_dict = self.create_products_dict(articles)
        customer_dict = self.create_customer_dict(
            first_name, last_name, patronymic_name, email, phone_number
        )

        return customer_dict, order_dict, products_dict
