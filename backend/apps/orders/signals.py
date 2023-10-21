from apps.orders.models import Order
from apps.utils import MessageSender
from apps.mail_sender.tasks import send_mail
from django.db.models.signals import m2m_changed
from django.dispatch import receiver


@receiver(m2m_changed, sender=Order.products.through)
def send_order_to_email(sender, instance, action, pk_set=None, **kwargs):
    """Вызов регистрации или обновления клиента в crm"""

    if action == 'post_add':
        data = {
            "customer": instance.customer.id,
            "products": [p.article for p in instance.products.all()],
        }
        message = (
            f"Успешно получен заказ: {instance.number} \n"
            f"Заказ от клиента: {instance.customer.last_name} {instance.customer.first_name} "
            f"{instance.customer.patronymic_name} \n"
            f"Отправляю товары на почту: {instance.customer.email}"
        )
        MessageSender().send_success_message(message)
        send_mail.delay(data)
