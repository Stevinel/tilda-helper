from django.db import models
from django.db.models import CharField, EmailField

from .managers import CustomerManager


class Customer(models.Model):
    """Модель покупателя"""

    objects = CustomerManager()

    email = EmailField("Почта", unique=True, blank=False)
    first_name = CharField("Имя", max_length=150, blank=True)
    last_name = CharField("Фамилия", max_length=150, blank=True)
    patronymic_name = CharField("Отчество", max_length=150, blank=True)
    phone_number = CharField("Телефон", max_length=20, blank=True)

    REQUIRED_FIELDS = 'email'

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"

    def __str__(self):
        return str(self.phone_number)
