from __future__ import absolute_import, unicode_literals

import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apps.customers.models import Customer
from apps.products.models import Pattern
from celery import shared_task
from django.template.loader import render_to_string


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 10, 'countdown': 5})
def send_mail(self, data):
    """Отправка файлов по товарам из заказа"""

    client = Customer.objects.filter(id=data['customer']).first()
    products = Pattern.objects.filter(article__in=data['products'])

    sender = os.getenv('EMAIL')
    to_addr = client.email
    email_password = os.getenv('EMAIL_TOKEN')

    message = MIMEMultipart()
    message['From'] = "{} <{}>".format("Hush Time", sender)
    message['To'] = to_addr
    message['Subject'] = 'Выкройки'
    html = render_to_string('email.html', context={'client_name': client.first_name})
    message.attach(MIMEText(html, 'html'))

    for pattern in products:
        pdf_attachment = MIMEApplication(pattern.pdf_file.read(), _subtype='pdf')
        pdf_attachment.add_header(
            'content-disposition', 'attachment', filename=f'{pattern.name}.pdf'
        )
        message.attach(pdf_attachment)

    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    server.login(sender, email_password)
    server.sendmail(sender, to_addr, message.as_string())
    server.quit()
