from django.db import models
from django.db.models import Count


class CustomerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(orders_count=Count("orders"))
