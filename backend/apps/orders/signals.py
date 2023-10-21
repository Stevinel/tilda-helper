from apps.orders.models import Order
from apps.utils import MessageSender
from apps.mail_sender.tasks import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Order)
def send_order_to_email(sender, instance, created, **kwargs):
    """Вызов регистрации или обновления клиента в crm"""

    products_exists = instance.products.all()

    if products_exists:
        data = {
            "customer": instance.customer.id,
            "products": [p.article for p in products_exists],
        }

        message = (
            f"Успешно получен заказ: {instance.number} \n"
            f"Заказ от клиента: {instance.customer.last_name} {instance.customer.first_name} "
            f"{instance.customer.patronymic_name} \n"
            f"Отправляю товары на почту: {instance.customer.email}"
        )
        MessageSender().send_success_message(message)
        send_mail.delay(data)
