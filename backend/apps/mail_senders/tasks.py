from __future__ import absolute_import, unicode_literals

import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from celery import shared_task
from sentry_sdk import capture_message
from celery.utils.log import get_task_logger

from apps.utils import Formatter, MessageSender
from apps.products.models import Pattern
from apps.customers.models import Customer

from django.template.loader import render_to_string


logger = get_task_logger(__name__)


API_NAME = os.getenv('API_NAME')
API_KEY = os.getenv('API_KEY')


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={'max_retries': 5},
    queue='send_mail',
)
def send_mail(self, data: dict):
    """Отправка писем с товарами из заказа"""
    client = Customer.objects.filter(id=data['customer']).first()
    products = Pattern.objects.filter(article__in=data['products'])
    full_name = Formatter.get_full_name_by_parts(client)

    if not products:
        return MessageSender().send_error_message(f'Не найдены товары для клиента {full_name}')

    sender = os.getenv('EMAIL')
    client_email = client.email
    email_token = os.getenv('EMAIL_TOKEN')

    message = MIMEMultipart()
    message['From'] = '{} <{}>'.format('Hush Time', sender)
    message['To'] = client_email
    message['Subject'] = 'Выкройки'
    html = render_to_string('email.html', context={'client': full_name})
    message.attach(MIMEText(html, 'html'))

    for pattern in products:
        if pattern.pdf_file:
            pdf_attachment = MIMEApplication(pattern.pdf_file.read(), _subtype='pdf')
            pdf_attachment.add_header(
                'content-disposition', 'attachment', filename=f'{pattern.name}.pdf'
            )
            message.attach(pdf_attachment)
        else:
            MessageSender().send_error_message(
                f'Не добавлен pdf file в товар: {pattern.name} \n'
                f'Заказ не будет доставлен на почту {client.email}'
            )
            return capture_message(f'Не добавлен pdf file в товар: {pattern.name}')

    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    server.login(sender, email_token)

    try:
        server.sendmail(sender, client_email, message.as_string())
        server.quit()
    except Exception as e:
        error = e.smtp_error.decode('utf-8') if hasattr(e, 'smtp_error') else e
        MessageSender().send_error_message(
            f'Ошибка отправки письма: {error}\n' f'Заказ не будет доставлен на почту {client.email}'
        )
        return capture_message(f'Mail send error: {e}')
    MessageSender().send_success_message(f'Заказ успешно отправлен на почту: {client.email}')


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=3600,
    retry_kwargs={'max_retries': 5},
    rate_limit='20/m',
    queue='send_many_mails',
)
def send_many_mails(self, data: dict):
    """Массовая рассылка клиентам"""

    sender = os.getenv('EMAIL_SENDER')
    email_token = os.getenv('EMAIL_SENDER_TOKEN')
    email_subject = data['subject']
    email_content = data['content']
    client_email = data['client_email']

    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    server.login(sender, email_token)

    message = MIMEMultipart('alternative')
    message['Content-Type'] = 'text/html; charset=utf-8'
    message['From'] = '{} <{}>'.format('Hush Time', sender)
    message['Subject'] = email_subject

    html = render_to_string('email_for_all.html', context={'html_data': email_content})
    message.attach(MIMEText(html, 'html', 'utf-8'))

    try:
        server.sendmail(sender, client_email, message.as_string())
    except smtplib.SMTPResponseException as e:
        if e.smtp_code == 451 and b'Ratelimit exceeded' in e.smtp_error:
            raise self.retry(exc=e, countdown=3600)
        else:
            capture_message(f'Mail sender error: {e}')
    except Exception as e:
        capture_message(f'Mail sender error: {e}')

    server.quit()
