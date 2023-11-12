from __future__ import absolute_import, unicode_literals

import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apps.customers.models import Customer
from apps.utils import MessageSender
from apps.products.models import Pattern
from celery import shared_task
from celery.utils.log import get_task_logger
from django.template.loader import render_to_string
from sentry_sdk import capture_message

logger = get_task_logger(__name__)


API_NAME = os.getenv("API_NAME")
API_KEY = os.getenv("API_KEY")


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 5})
def send_mail(self, data):
    """Отправка файлов по товарам из заказа"""

    client = Customer.objects.filter(id=data["customer"]).first()
    products = Pattern.objects.filter(article__in=data["products"])
    full_name = " ".join([client.last_name, client.first_name, client.patronymic_name]).rstrip()

    if not products:
        return MessageSender().send_error_message(f"Не найдены товары для клиента {full_name}")

    sender = os.getenv("EMAIL")
    client_email = client.email
    email_token = os.getenv("EMAIL_TOKEN")

    message = MIMEMultipart()
    message["From"] = "{} <{}>".format("Hush Time", sender)
    message["To"] = client_email
    message["Subject"] = "Выкройки"
    html = render_to_string("email.html", context={"client": full_name})
    message.attach(MIMEText(html, "html"))

    for pattern in products:
        if pattern.pdf_file:
            pdf_attachment = MIMEApplication(pattern.pdf_file.read(), _subtype="pdf")
            pdf_attachment.add_header(
                "content-disposition", "attachment", filename=f"{pattern.name}.pdf"
            )
            message.attach(pdf_attachment)
        else:
            MessageSender().send_error_message(
                f"Не добавлен pdf file в товар: {pattern.name} \n"
                f"Заказ не будет доставлен на почту {client.email}"
            )
            return capture_message(f"Не добавлен pdf file в товар: {pattern.name}")

    server = smtplib.SMTP_SSL("smtp.mail.ru", 465)
    server.login(sender, email_token)

    try:
        server.sendmail(sender, client_email, message.as_string())
        server.quit()
    except Exception as e:
        error = e.smtp_error.decode('utf-8') if hasattr(e, 'smtp_error') else e
        MessageSender().send_error_message(
            f"Ошибка отправки письма: {error}\n"
            f"Заказ не будет доставлен на почту {client.email}"
        )
        return capture_message(f"Mail error: {e}")
    MessageSender().send_success_message(f"Заказ успешно отправлен на почту: {client.email}")