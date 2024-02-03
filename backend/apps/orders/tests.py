import os
import json

from unittest.mock import ANY, patch

from apps.orders.models import Order
from apps.orders.manager import DataManager
from apps.orders.webhook import WebhookView
from apps.products.models import Pattern
from apps.customers.models import Customer
from apps.orders.serializers import WebhookSerializer

from django.test import TestCase, RequestFactory, SimpleTestCase
from django.urls import resolve, reverse


class OrderModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Создаем тестового клиента и продукт"""

        cls.customer = Customer.objects.create(email='customer@example.com')
        cls.product = Pattern.objects.create(article=123456, name='Test Pattern', price=123)

        # Создаем тестовый заказ
        cls.order = Order.objects.create(number=123456, payment_amount=1000, customer=cls.customer)
        cls.order.products.add(cls.product)

    def test_order_creation(self):
        """Проверка создания заказа"""

        self.assertTrue(isinstance(self.order, Order))
        self.assertEqual(self.order.__str__(), f'Номер заказа: {self.order.number}')

    def test_order_fields(self):
        """Проверка полей заказа"""

        self.assertEqual(self.order.number, 123456)
        self.assertEqual(self.order.payment_amount, 1000)
        self.assertEqual(self.order.customer, self.customer)
        self.assertIn(self.product, self.order.products.all())

    def test_order_relationships(self):
        """Проверка связей модели заказа"""

        self.assertEqual(self.order.customer.email, 'customer@example.com')
        self.assertEqual(self.order.products.count(), 1)
        self.assertEqual(self.order.products.first(), self.product)


class OrdersUrlsTest(SimpleTestCase):
    def test_webhook_url_resolves(self):
        """Тестирование URL 'webhook/'"""

        url = reverse('webhook')
        self.assertEqual(resolve(url).func.view_class, WebhookView)


class WebhookSerializerTest(TestCase):
    def setUp(self):
        self.serializer = WebhookSerializer()
        self.sample_data = {
            'Name': 'Иванов Иван Иванович',
            'Phone': '+7 (123) 456-78-90',
            'Email': 'test@example.com',
            'payment': {
                'amount': '1000',
                'orderid': '123456',
                'products': [
                    {'name': 'Product 1', 'price': '500', 'sku': '123456'},
                ],
            },
        }

    def test_serialize(self):
        """Тест сериалайзера"""

        customer_dict, order_dict, products_dict = self.serializer.serialize(self.sample_data)

        # Проверка данных клиента
        self.assertEqual(customer_dict['customer']['first_name'], 'Иван')
        self.assertEqual(customer_dict['customer']['last_name'], 'Иванов')
        self.assertEqual(customer_dict['customer']['patronymic_name'], 'Иванович')
        self.assertEqual(customer_dict['customer']['email'], 'test@example.com')
        self.assertEqual(customer_dict['customer']['phone_number'], '+7 (123) 456-78-90')

        # Проверка данных заказа
        self.assertEqual(order_dict['order']['order_number'], '123456')
        self.assertEqual(order_dict['order']['payment_amount'], 1000)

        # Проверка данных продуктов
        self.assertEqual(len(products_dict), 1)
        self.assertEqual(products_dict['products'][0]['article'], '123456')
        self.assertEqual(products_dict['products'][0]['quantity'], 1)


class DataManagerTestCase(TestCase):
    def setUp(self):
        """Подготовка данных"""

        self.customer_info = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'patronymic_name': 'Иванович',
            'email': 'ivan@example.com',
            'phone_number': '1234567890',
        }
        self.order_info = {'order_number': '123', 'payment_amount': 1000}
        self.products_info = [{'article': '123456'}, {'article': '123457'}]

        self.customer = Customer.objects.create(**self.customer_info)
        self.order = Order.objects.create(
            number=self.order_info['order_number'],
            payment_amount=self.order_info['payment_amount'],
            customer=self.customer,
        )
        self.products = [
            Pattern.objects.create(article=prod['article'], price=123)
            for prod in self.products_info
        ]

        self.manager = DataManager(
            customer={'customer': self.customer_info},
            order={'order': self.order_info},
            products={'products': self.products_info},
        )

    @patch('apps.customers.models.Customer.objects.get')
    @patch('apps.customers.models.Customer.objects.create')
    def test_save_customer(self, mock_create, mock_get):
        """Тест создания\сохранения клиента"""

        mock_get.side_effect = Customer.DoesNotExist
        mock_create.return_value = self.customer

        saved_customer = self.manager.save_customer()

        mock_create.assert_called_once_with(**self.customer_info)
        self.assertEqual(saved_customer.email, self.customer.email)

    def test_save_order(self):
        """Тест сохранения заказа"""

        saved_order = self.manager.save_order(self.customer)

        self.assertEqual(saved_order.number, self.order.number)
        self.assertEqual(saved_order.customer, self.customer)

    @patch('apps.products.models.Pattern.objects.filter')
    def test_save_products(self, mock_filter):
        """Тест сохранения товаров"""

        mock_filter.return_value = self.products

        saved_products = self.manager.save_products(self.order)

        mock_filter.assert_called_once_with(
            article__in=[prod['article'] for prod in self.products_info]
        )
        self.assertEqual(list(saved_products), self.products)

    @patch('apps.orders.manager.DataManager.send_order_data')
    def test_save_data(self, mock_send_order_data):
        """Сохранение данных"""

        with patch.object(
            self.manager, 'save_customer', return_value=self.customer
        ) as mock_save_customer, patch.object(
            self.manager, 'save_order', return_value=self.order
        ) as mock_save_order, patch.object(
            self.manager, 'save_products', return_value=self.products
        ) as mock_save_products:
            self.manager.save_data()

            mock_save_customer.assert_called_once()
            mock_save_order.assert_called_once_with(self.customer)
            mock_save_products.assert_called_once_with(self.order)
            mock_send_order_data.assert_called_once_with(self.order, self.customer, self.products)


class WebhookViewTestCase(TestCase):
    def setUp(self):
        """Подготовка данных"""

        API_NAME = os.getenv('API_NAME')
        API_KEY = os.getenv('API_KEY')
        self.factory = RequestFactory()
        self.view = WebhookView.as_view()
        self.data = {
            API_NAME: API_KEY,
            'Name': 'Иванов Иван Иванович',
            'Phone': '+7 (123) 456-78-90',
            'Email': 'test@example.com',
            'payment': {
                'amount': '1000',
                'orderid': '123456',
                'products': [
                    {'name': 'Product 1', 'price': '500', 'sku': '123456'},
                ],
            },
        }
        self.serialized_customer = {
            'customer': {
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'patronymic_name': 'Иванович',
                'email': 'test@example.com',
                'phone_number': '+7 (123) 456-78-90',
            }
        }
        self.serialized_order = {'order': {'order_number': '123456', 'payment_amount': 1000}}
        self.serialized_product = {'products': [{'article': '123456', 'quantity': 1}]}

        self.customer_info = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'patronymic_name': 'Иванович',
            'email': 'ivan@example.com',
            'phone_number': '+7 (123) 456-78-90',
        }
        self.order_info = {'order_number': '123456', 'payment_amount': 1000}

        self.customer = Customer.objects.create(**self.customer_info)
        self.order = Order.objects.create(
            number=self.order_info['order_number'],
            payment_amount=self.order_info['payment_amount'],
            customer=self.customer,
        )
        Pattern.objects.create(article='123456', price=123)
        self.products = Pattern.objects.filter(article='123456')

    def test_access_verification_failure(self):
        """Тест декоратора"""

        invalid_data = {'wrong_api_name': 'invalid_key'}
        request = self.factory.post(
            '/webhook/', json.dumps(invalid_data), content_type='application/json'
        )

        view = WebhookView()
        response = view.post(request)
        self.assertEqual(response.content.decode('utf8'), '{"error": "Access denied"}')

    @patch('apps.orders.manager.DataManager.send_order_data')
    @patch('apps.orders.webhook.WebhookSerializer')
    def test_post_success(self, mock_serializer, mock_send_order_data):
        """Тест успеха вебхука"""

        mock_serializer.return_value.serialize.return_value = (
            self.serialized_customer,
            self.serialized_order,
            self.serialized_product,
        )

        request = self.factory.post(
            '/webhook/', json.dumps(self.data), content_type='application/json'
        )

        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf8'), '{}')
        mock_send_order_data.assert_called_once_with(ANY, ANY, ANY)

    @patch('apps.orders.webhook.WebhookSerializer')
    @patch('apps.utils.MessageSender.send_error_message')
    def test_post_serialization_error(self, mock_serializer, mock_send_message):
        """Тест ошибки сериализации"""

        mock_serializer.return_value.serialize.side_effect = Exception('Serialization error')
        request = self.factory.post(
            '/webhook/', json.dumps(self.data), content_type='application/json'
        )

        response = self.view(request)
        self.assertEqual(response.content.decode('utf8'), '{"error": "Data serialization error"}')
        mock_send_message.assert_called_once()
