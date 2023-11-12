from apps.utils import Formatter


class WebhookSerializer(Formatter):
    """Сериализация данных, полученных в вебхуке"""

    def serialize(self, data: dict) -> tuple:
        """Сериализация входящих данных из вебхука тильды"""

        last_name, first_name, patronymic_name = self.format_full_namme(data["Name"])
        phone = self.format_phone(data["Phone"])
        email = self.format_email(data["Email"])
        payment_amount = self.format_payment(data["payment"]["amount"])
        order_number = data["payment"]["orderid"]
        products_data = data["payment"]["products"]

        order_dict = self.create_order_dict(order_number, payment_amount)
        products_dict = self.create_products_dict(products_data)
        customer_dict = self.create_customer_dict(
            first_name, last_name, patronymic_name, email, phone
        )

        return customer_dict, order_dict, products_dict
