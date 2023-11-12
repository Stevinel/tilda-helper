import re

from apps.utils import PhoneFormatter


class TgSerializer(PhoneFormatter):
    """Сериализация данных, полученных из ТГ"""

    def serialize(self, message):
        """Сериализация входящих данных из ТГ"""

        payment_amount = None
        first_name = None
        last_name = None
        patronymic_name = None
        email = None
        phone_number = None

        order_match = re.search(r'Order #(\d+)', message.text)
        if order_match:
            order_number = order_match.group(1)

            article_matches = re.findall(r'\d{6},', message.text) # only 6 numbers article
            articles = [article.rstrip(',') for article in article_matches]

            payment_match = re.search(r'Payment Amount: (\d+(\.\d+)?) RUB', message.text)

            if payment_match:
                payment_amount = payment_match.group(1)
                payment_amount = payment_amount.replace(',', '.')

            name_match = re.search(r'Name: (.+)', message.text)
            if name_match:
                full_name = name_match.group(1).split()
                if len(full_name) >= 1:
                    last_name = full_name[0]
                if len(full_name) >= 2:
                    first_name = full_name[1]
                if len(full_name) >= 3:
                    patronymic_name = full_name[2]

            email_match = re.search(r'Email: (.+)', message.text)
            if email_match:
                email = email_match.group(1)

            phone_match = re.search(r'Phone: (.+)', message.text)
            if phone_match:
                phone_number = self.get_phone(phone_match.group(1))
        else:
            return

        customer = {
            "customer": {
                "first_name": first_name if first_name else "",
                "last_name":last_name if last_name else "",
                "patronymic_name": patronymic_name if patronymic_name else "",
                "email": email,
                "phone_number": phone_number,
            }
        }

        order = {
            "order": {
                "order_number": order_number,
                "payment_amount": int(payment_amount),
            }
        }

        products = {"products": []}

        for art in articles:
            product = {
                "article": art,
                "quantity": 1, # by default
            }
            products["products"].append(product)

        return customer, order, products
