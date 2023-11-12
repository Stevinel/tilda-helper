from django.db import transaction
from django.db import IntegrityError, OperationalError

from ..customers.models import Customer
from ..mail_sender.tasks import send_mail
from ..orders.models import Order
from ..products.models import Pattern
from ..utils import MessageSender

from sentry_sdk import capture_exception


class DataSender:
    """Класс отвечающий за отправку сохранённых данных"""

    @staticmethod
    def send_order_data(order: Order, customer: Customer, order_products: Pattern) -> None:
        data = {
            "customer": customer.id,
            "products": [p.article for p in order_products],
        }
        message = (
            f"Успешно получен заказ: {order.number} \n"
            f"Заказ от клиента: {customer.last_name} {customer.first_name} "
            f"{customer.patronymic_name} \n"
            f"Отправляю товары на почту: {customer.email}"
        )
        MessageSender().send_success_message(message)
        send_mail.delay(data)


class DataManager(DataSender):
    """Класс отвечающая за сохранение данных полученных на вебхуке или тг"""

    def __init__(self, customer: dict, order: dict, products: dict):
        self.customer = customer["customer"]
        self.order = order["order"]
        self.products = products["products"]

    @transaction.atomic
    def save_data(self) -> None:
        """Общий метод отвечающий за сохранение данных в БД"""

        try:
            customer = self.save_customer()
            order = self.save_order(customer)
            order_products = self.save_products(order)

            self.send_order_data(order, customer, order_products)
        except (IntegrityError, OperationalError) as e:
            capture_exception(e)
            message = f"Ошибка сохранения заказа: {order.number}"
            MessageSender().send_error_message(message)

    def save_customer(self) -> Customer:
        """Сохранение клиента в БД"""

        try:
            customer = Customer.objects.get(email=self.customer["email"])
            if customer.phone_number != self.customer["phone_number"]:
                customer.phone_number = self.customer["phone_number"]
                customer.save()
        except Customer.DoesNotExist:
            customer = Customer.objects.create(
                first_name=self.customer["first_name"],
                last_name=self.customer["last_name"],
                patronymic_name=self.customer["patronymic_name"],
                email=self.customer["email"],
                phone_number=self.customer["phone_number"],
            )
        return customer

    def save_order(self, customer: Customer) -> None:
        """Сохранение заказа в БД"""

        order = Order.objects.create(
            number=self.order["order_number"],
            payment_amount=self.order["payment_amount"],
            customer=customer,
        )
        order.save()
        return order

    def save_products(self, order: Order) -> Pattern:
        """Сохранение товаров к заказу в БД"""

        products_articles = [p["article"] for p in self.products]
        products = Pattern.objects.filter(article__in=products_articles)
        order.products.set(products)
        return products
