from .models import Customer

from django.db import IntegrityError
from django.test import TestCase


class CustomerModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Установка тестовых данных для всех методов"""

        cls.customer = Customer.objects.create(
            email='customer@example.com',
            first_name='Иван',
            last_name='Иванов',
            patronymic_name='Иванович',
            phone_number='1234567890',
        )

    def test_customer_creation(self):
        """Тест на создание покупателя"""

        self.assertIsInstance(self.customer, Customer)

    def test_string_representation(self):
        """Тест строкового представления"""

        self.assertEqual(str(self.customer), self.customer.phone_number)

    def test_email_uniqueness(self):
        """Тест на уникальность почты"""

        with self.assertRaises(IntegrityError):
            Customer.objects.create(
                email='customer@example.com',  # Такой же email, как у существующего пользователя
                first_name='Анна',
                last_name='Каренина',
                phone_number='0987654321',
            )

    def test_is_receive_mails_default(self):
        """Тест на значение по умолчанию для получения рассылки"""

        new_customer = Customer()
        self.assertTrue(new_customer.is_receive_mails)

    def test_sum_old_orders_blank(self):
        """Тест на возможность оставить sum_old_orders пустым"""

        new_customer = Customer(email='newcustomer@example.com')
        new_customer.full_clean()  # Не должно вызвать исключение
        self.assertIsNone(new_customer.sum_old_orders)
