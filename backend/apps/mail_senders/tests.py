import base64
import re
from smtplib import SMTPException
from unittest.mock import MagicMock, patch

from apps.customers.models import Customer
from apps.mail_senders.tasks import send_mail, send_many_mails
from apps.products.models import Pattern
from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings

from .models import MailSender


class MailSenderModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создаём объект MailSender"""

        cls.mail_sender = MailSender.objects.create(
            subject='Test Subject',
            content='Test content.'
        )

    def test_create_mail_sender(self):
        """Тест проверяет, что объект MailSender был создан"""

        self.assertIsInstance(self.mail_sender, MailSender)

    def test_default_is_active(self):
        """Тест проверяет значение по умолчанию для поля is_active"""

        self.assertFalse(self.mail_sender.is_active)

    def test_updated_at(self):
        """Тест проверяет, что поле updated_at автоматически обновляется"""

        old_updated_at = self.mail_sender.updated_at
        self.mail_sender.save()
        self.mail_sender.refresh_from_db()
        self.assertTrue(self.mail_sender.updated_at > old_updated_at)

    def test_string_representation(self):
        """Тест проверяет корректное строковое представление объекта"""

        self.assertEqual(str(self.mail_sender), f'Тема письма: {self.mail_sender.subject}')


class SendMailTaskTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаем тестовые данные для клиента
        cls.customer = Customer.objects.create(
            email="customer@example.com",
            first_name="Test",
            last_name="Customer"
        )

        # Создаем тестовые данные для продукта
        pdf_file = ContentFile(
            b"PDF file content",
            name="test.pdf"
        )
        cls.pattern = Pattern.objects.create(
            article=123456,
            pdf_file=pdf_file,
            name="Test Pattern",
            price=123
        )

    @patch('apps.mail_senders.tasks.smtplib.SMTP_SSL')
    @patch('apps.mail_senders.tasks.capture_message')
    @patch('apps.mail_senders.tasks.MessageSender.send_error_message')
    @patch('apps.mail_senders.tasks.MessageSender.send_success_message')
    def test_send_mail(self, mock_success_msg, mock_error_msg, mock_capture_msg, mock_smtp):
        # Подготовка данных для отправки
        data = {
            "customer": self.customer.id,
            "products": [self.pattern.article]
        }

        # Создание моковых объектов для SMTP и проверка вызова функции отправки сообщения
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        # Вызов тестируемой функции
        send_mail(data)

        # Проверяем, что была попытка отправки сообщения
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()

        # Проверяем, что не было ошибок при отправке сообщения
        mock_error_msg.assert_not_called()
        mock_capture_msg.assert_not_called()

        # Проверяем, что было отправлено сообщение об успешной отправке
        mock_success_msg.assert_called_once()

        # Проверка, что сообщение сформировано правильно
        _, args, _ = mock_server.sendmail.mock_calls[0]
        from_email, to_email, message_str = args
        self.assertIn("From: Hush Time <", message_str)
        self.assertIn("To: customer@example.com", message_str)

        # Проверка, что тема сообщения присутствует в закодированном виде
        expected_subject_encoded = base64.b64encode('Выкройки'.encode('utf-8')).decode('utf-8')
        expected_subject_mime = f"=?utf-8?b?{expected_subject_encoded}?="
        self.assertIn(expected_subject_mime, message_str)

        # Проверка, что в сообщении есть вложение
        pattern_attachment = re.compile(r"filename=\"Test Pattern\.pdf\"")
        self.assertTrue(pattern_attachment.search(message_str),
                        "PDF attachment header not found in message")


class SendManyMailsTaskTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаем тестовых клиентов
        Customer.objects.create(email="test@test.ru", is_receive_mails=True)
        Customer.objects.create(email="real_customer@example.com", is_receive_mails=True)

    @patch('apps.mail_senders.tasks.smtplib.SMTP_SSL')
    @patch('apps.mail_senders.tasks.capture_message')
    @patch('apps.mail_senders.tasks.MessageSender.send_success_message')
    def test_send_many_mails(self, mock_success_msg, mock_capture_msg, mock_smtp):
        # Параметры для тестирования
        data = {"subject": "Test Subject", "content": "Test Content"}

        # Создание мокового объекта для SMTP сервера
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        # Вызов функции для тестирования
        send_many_mails(data)

        # Проверяем, была ли вызвана функция sendmail
        self.assertTrue(mock_server.sendmail.called, "sendmail was not called")

        # Проверка сообщения об успехе
        mock_success_msg.assert_called_once()
        success_message = mock_success_msg.call_args[0][0]
        self.assertIn("Кол-во отправленных писем: 1", success_message)
