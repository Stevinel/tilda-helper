import os

from django.db import transaction

from ..customers.models import Customer
from ..orders.models import Order
from ..products.models import Pattern
from .tasks import send_mail


class WebhookDataManager:
    """Модель отвечающая за данные, полученные на вебхуке"""

    def __init__(self, customer, order, products):
        self.customer = customer['customer']
        self.order = order['order']
        self.products = products['products']

    @transaction.atomic
    def save_data(self):
        customer = self.save_customer()
        self.save_order(customer)

    def save_customer(self):
        customer, _ = Customer.objects.get_or_create(
            first_name=self.customer['first_name'],
            last_name=self.customer['last_name'],
            patronymic_name=self.customer['patronymic_name'],
            email=self.customer['email'],
            phone_number=self.customer['phone_number'],
        )
        return customer

    def save_order(self, customer):
        products_articles = [p['article'] for p in self.products]
        products = Pattern.objects.filter(article__in=products_articles)
        order = Order.objects.create(
            number=self.order['order_number'],
            payment_amount=self.order['payment_amount'],
            customer=customer,
        )
        order.save()
        order.products.set(products)
        order.save()

        data = {'customer': customer.id, 'products': [p.article for p in products]}
        send_mail.delay(data)
