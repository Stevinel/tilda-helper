from django.db import models
from django.db.models import PositiveIntegerField

from ..customers.models import Customer


class Order(models.Model):
    """Модель заказа"""

    number = PositiveIntegerField("Номер заказа", blank=False)
    payment_amount = PositiveIntegerField("Сумма заказа", blank=False)
    products = models.ManyToManyField(
        "products.Pattern", related_name="orders", verbose_name="Товары"
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Покупатель",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Номер заказа: {self.number}"
