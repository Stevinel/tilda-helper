class WebhookSerializer:
    """Сериализация данных, полученных в вебхуке"""

    def serialize(self, data):
        """Сериализация входящих данных из вебхука тильды"""

        name_parts = data["Name"].split()

        email = data["Email"]
        if email.endswith("gmail.ru"):
            email = email.replace("gmail.ru", "gmail.com")

        customer = {
            "customer": {
                "first_name": name_parts[0] if len(name_parts) >= 1 else "",
                "last_name": name_parts[1] if len(name_parts) >= 2 else "",
                "patronymic_name": name_parts[-1] if len(name_parts) == 3 else "",
                "email": email,
                "phone_number": data["Phone"],
            }
        }

        order = {
            "order": {
                "order_number": data["payment"]["orderid"],
                "payment_amount": data["payment"]["amount"],
            }
        }

        products = {"products": []}

        for product_data in data["payment"]["products"]:
            product = {
                "article": product_data["sku"],
                "quantity": product_data["quantity"],
            }
            products["products"].append(product)

        return customer, order, products
