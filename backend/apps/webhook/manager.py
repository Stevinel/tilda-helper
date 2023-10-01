from django.db import transaction

from ..customers.models import Customer
from ..orders.models import Order
from ..products.models import Pattern


class WebhookDataManager:
    """Модель отвечающая за данные полученные на вебхуке"""

    def __init__(self, customer, order, products):
        self.customer = customer["customer"]
        self.order = order["order"]
        self.products = products["products"]

    @transaction.atomic
    def save_data(self) -> None:
        """Общий метод отвечающий за сохранение данных в БД"""

        customer = self.save_customer()
        self.save_order(customer)

    def save_customer(self) -> Customer:
        """Сохранение клиента в БД"""

        try:
            customer = Customer.objects.get(email=self.customer["email"])
        except Customer.DoesNotExist:
            customer = Customer.objects.create(
                first_name=self.customer["first_name"],
                last_name=self.customer["last_name"],
                patronymic_name=self.customer["patronymic_name"],
                email=self.customer["email"],
                phone_number=self.customer["phone_number"],
            )
        return customer

    def save_order(self, customer) -> None:
        """Сохранение заказа в БД"""

        products_articles = [p["article"] for p in self.products]
        products = Pattern.objects.filter(article__in=products_articles)
        order = Order.objects.create(
            number=self.order["order_number"],
            payment_amount=self.order["payment_amount"],
            customer=customer,
        )
        order.save()
        order.products.set(products)
        order.save()
