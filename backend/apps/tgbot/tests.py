import os
from unittest.mock import patch

from apps.tgbot.serializers import TgSerializer
from django.test import TestCase
from fastapi.testclient import TestClient
from telebot.types import Message

from .fastapp import app
from .main import TARGET_CHAT_ID


class TgSerializerTestCase(TestCase):

    def setUp(self):
        """Настройки"""

        self.serializer = TgSerializer()

    def test_search_payment_amount(self):
        text = "Payment Amount: 1000 RUB"
        result = self.serializer.search_payment_amount(text)
        self.assertEqual(result, 1000)

    def test_search_articles(self):
        text = "Article numbers: 123456, 654321,"
        result = self.serializer.search_articles(text)
        self.assertEqual(result, ['123456', '654321'])

    def test_search_full_name(self):
        text = "Name: Ivan Ivanov Ivanovich"
        result = self.serializer.search_full_name(text)
        self.assertEqual(result, ('Ivan', 'Ivanov', 'Ivanovich'))

    def test_search_email(self):
        text = "Email: test@example.com"
        result = self.serializer.search_email(text)
        self.assertEqual(result, 'test@example.com')

    def test_search_phone(self):
        text = "Phone: +1234567890"
        result = self.serializer.search_phone(text)
        self.assertEqual(result, '+7 (123) 456-78-90')

    def test_serialize(self):
        message = Message(123456, 123456, '19.11.2023', 123456, 123456, [], '12345')
        message.text = (
            "Order #123456 Payment Amount: 1000 RUB "
            "Name: Ivan Ivanov Ivanovich Email: test@example.com "
            "Phone: +1234567890 Article numbers: 123456, 654321,"
        )
        customer_dict, order_dict, products_dict = self.serializer.serialize(message)

        self.assertIsNotNone(customer_dict)
        self.assertIsNotNone(order_dict)
        self.assertIsNotNone(products_dict)
        self.assertEqual(order_dict['order']['order_number'], '123456')
        self.assertEqual(customer_dict['customer']['first_name'], 'Ivan')
        self.assertEqual(products_dict['products'], [{'article': '123456', 'quantity': 1}, {'article': '654321', 'quantity': 1}])


class FastAppTestCase(TestCase):

    def setUp(self):
        """Настройка данных"""

        self.client = TestClient(app)
        API_NAME = os.getenv("API_NAME")
        API_KEY = os.getenv("API_KEY")

        self.api_name = API_NAME
        self.api_key = API_KEY

    @patch('apps.tgbot.fastapp.BOT')
    def test_send_error_access_denied(self, mock_bot):
        response = self.client.post("/notification/send_error/", json={})
        self.assertDictEqual(response.json(), {"error": "Access denied"})
        mock_bot.send_message.assert_not_called()

    @patch('apps.tgbot.fastapp.BOT')
    def test_send_error_success(self, mock_bot):
        valid_data = {self.api_name: self.api_key, "message": "Test error message"}
        response = self.client.post("/notification/send_error/", json=valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {"success": True})
        mock_bot.send_message.assert_called_once_with(TARGET_CHAT_ID, "Test error message")

    @patch('apps.tgbot.fastapp.BOT')
    def test_send_message_access_denied(self, mock_bot):
        response = self.client.post("/notification/send_message/", json={})
        self.assertDictEqual(response.json(), {"error": "Access denied"})
        mock_bot.send_message.assert_not_called()

    @patch('apps.tgbot.fastapp.BOT')
    def test_send_message_success(self, mock_bot):
        valid_data = {self.api_name: self.api_key, "message": "Test success message"}
        response = self.client.post("/notification/send_message/", json=valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {"success": True})
        mock_bot.send_message.assert_called_once_with(TARGET_CHAT_ID, "Test success message")
