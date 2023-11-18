from django.db import models


class MailSender(models.Model):
    """Модель рассылки писем"""

    subject = models.CharField("Тема письма", blank=False)
    content = models.TextField("Содержимое письма", blank=False)
    is_active = models.BooleanField("Активен", default=False)
    updated_at = models.DateTimeField("Дата изменения", auto_now=True)

    class Meta:
        verbose_name = "Рассыльщик"
        verbose_name_plural = "Рассыльщики"

    def __str__(self):
        return f"Тема письма: {self.subject}"