from unittest.mock import patch

from .utils import Formatter, MessageSender
from .customers.models import Customer

from django.test import TestCase


class FormatterTestCase(TestCase):
    def test_format_phone(self):
        self.assertEqual(Formatter.format_phone('+7 (123) 456-78-90'), '+7 (123) 456-78-90')

    def test_format_email(self):
        self.assertEqual(Formatter.format_email('test@gmail.ru'), 'test@gmail.com')

    def test_format_full_name(self):
        self.assertEqual(
            Formatter.format_full_name('Ivanov Ivan Ivanovich'), ('Ivanov', 'Ivan', 'Ivanovich')
        )

    def test_format_payment(self):
        self.assertEqual(Formatter.format_payment('1000.50'), 1000)
        self.assertEqual(Formatter.format_payment({'payment': {'amount': '2000.75'}}), 2000)

    def test_create_customer_dict(self):
        customer_dict = Formatter.create_customer_dict(
            'Ivan', 'Ivanov', 'Ivanovich', 'test@example.com', '+1234567890'
        )
        expected = {
            'customer': {
                'first_name': 'Ivan',
                'last_name': 'Ivanov',
                'patronymic_name': 'Ivanovich',
                'email': 'test@example.com',
                'phone_number': '+1234567890',
            }
        }
        self.assertDictEqual(customer_dict, expected)

    def test_create_order_dict(self):
        order_dict = Formatter.create_order_dict('123456', 1000)
        expected = {
            'order': {
                'order_number': '123456',
                'payment_amount': 1000,
            }
        }
        self.assertDictEqual(order_dict, expected)

    def test_create_products_dict(self):
        products_dict = Formatter.create_products_dict([{'sku': '123456', 'quantity': 2}, '654321'])
        expected = {
            'products': [
                {'article': '123456', 'quantity': 2},
                {'article': '654321', 'quantity': 1},  # default_quantity используется здесь
            ]
        }
        self.assertDictEqual(products_dict, expected)

    def test_get_full_name_by_parts(self):
        client = Customer(first_name='Ivan', last_name='Ivanov', patronymic_name='Ivanovich')
        full_name = Formatter.get_full_name_by_parts(client)
        self.assertEqual(full_name, 'Ivanov Ivan Ivanovich')


class MessageSenderTestCase(TestCase):
    @patch('requests.post')
    def test_send_success_message(self, mock_post):
        mock_post.return_value.status_code = 200
        sender = MessageSender()
        sender.send_success_message('Test message')
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_send_error_message(self, mock_post):
        mock_post.return_value.status_code = 200
        sender = MessageSender()
        sender.send_error_message('Test error message')
        mock_post.assert_called_once()
