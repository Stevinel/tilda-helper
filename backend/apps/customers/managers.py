from django.contrib.auth.models import UserManager
from django.db.models import Count


class CustomerManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().annotate(orders_count=Count("orders"))
