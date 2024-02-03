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
