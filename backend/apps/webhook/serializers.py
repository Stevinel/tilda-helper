class WebhookSerializer:
    """Сериализация данных, полученных в вебхуке"""

    def serialize(self, data):
        name_parts = data['Name'].split()
        customer = {
            'customer': {
                'first_name': name_parts[1] if len(name_parts) >= 1 else '',
                'last_name': name_parts[0] if len(name_parts) >= 2 else '',
                'patronymic_name': name_parts[-1] if len(name_parts) == 3 else '',
                'email': data['Email'],
                'phone_number': data['Phone'],
            }
        }

        order = {'order': {'order_number': data['payment']['orderid'], 'payment_amount': 0}}

        products = {'products': []}

        for product_data in data['payment']['products']:
            product = {'article': product_data['sku'], 'quantity': product_data['quantity']}
            products['products'].append(product)
            order['order']['payment_amount'] += product_data['amount']

        return customer, order, products