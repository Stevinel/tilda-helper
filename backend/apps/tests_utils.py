from unittest.mock import patch

from django.test import TestCase

from .utils import Formatter, MessageSender


class FormatterTestCase(TestCase):

    def test_format_phone(self):
        self.assertEqual(Formatter.format_phone("+7 (123) 456-78-90"), "+7 (123) 456-78-90")

    def test_format_email(self):
        self.assertEqual(Formatter.format_email("test@gmail.ru"), "test@gmail.com")

    def test_format_full_name(self):
        self.assertEqual(Formatter.format_full_name("Ivanov Ivan Ivanovich"), ("Ivanov", "Ivan", "Ivanovich"))

class MessageSenderTestCase(TestCase):

    @patch('requests.post')
    def test_send_success_message(self, mock_post):
        mock_post.return_value.status_code = 200
        sender = MessageSender()
        sender.send_success_message("Test message")
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_send_error_message(self, mock_post):
        mock_post.return_value.status_code = 200
        sender = MessageSender()
        sender.send_error_message("Test error message")
        mock_post.assert_called_once()
