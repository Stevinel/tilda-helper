from datetime import timedelta

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Sum
from django.utils.timezone import now

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"
        widgets = {
            "products": FilteredSelectMultiple("выкройки", is_stacked=False),
        }


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    list_display = (
        "number",
        "payment_amount",
        "customer",
        "created_at",
    )
    search_fields = (
        "number",
        "payment_amount",
        "customer__phone_number",
        "products__article",
        "products__name",
    )
    list_filter = ("payment_amount", "products")
    empty_value_display = "-пусто-"
    autocomplete_fields = ["customer"]

    change_list_template = 'custom_change_list.html'

    def changelist_view(self, request, extra_context=None):
        # Вычисляем статистику за сегодня
        today = now().date()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)

        # Статистика за сегодня
        today_stats = {
            'total': Order.objects.filter(
                created_at__gte=today,
                created_at__lt=tomorrow).count(),
            'sum':
                Order.objects.filter(
                    created_at__gte=today,
                    created_at__lt=tomorrow)
                .aggregate(
                    sum=Sum('payment_amount'))['sum'] or 0
        }

        # Статистика за вчера
        yesterday_stats = {
            'total': Order.objects.filter(
                created_at__gte=yesterday,
                created_at__lt=today).count(),
            'sum':
                Order.objects.filter(
                    created_at__gte=yesterday,
                    created_at__lt=today)
                .aggregate(
                    sum=Sum('payment_amount'))['sum'] or 0
        }

        extra_context = extra_context or {}
        extra_context['today_stats'] = today_stats
        extra_context['yesterday_stats'] = yesterday_stats

        return super().changelist_view(request, extra_context=extra_context)