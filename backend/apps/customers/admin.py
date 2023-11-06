from django.contrib import admin
from django.db.models import Count, Sum, F, Value
from django.db.models.functions import Coalesce
from django_admin_inline_paginator.admin import TabularInlinePaginated

from ..orders.models import Order
from .models import Customer


class OrderCountFilter(admin.SimpleListFilter):
    """Сортировка по кол-ву заказов"""

    title = "Кол-во заказов"
    parameter_name = "orders_count"

    def lookups(self, request, model_admin):
        return (
            ("asc", "По возрастанию"),
            ("desc", "По убыванию"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        queryset = queryset.annotate(orders_count=Count("orders"))

        if value == "asc":
            return queryset.order_by("orders_count")
        elif value == "desc":

            return queryset.order_by("-orders_count")
        return queryset


class OrderSumFilter(admin.SimpleListFilter):
    """Сортировка по сумме заказов"""

    title = "Сумма заказов"
    parameter_name = "orders_sum"

    def lookups(self, request, model_admin):
        return (
            ("asc", "По возрастанию"),
            ("desc", "По убыванию"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        queryset = queryset.annotate(
            orders_sum=Coalesce(Sum('orders__payment_amount'), Value(0)) + F('sum_old_orders')
        )

        if value == "asc":
            return queryset.order_by("orders_sum")
        elif value == "desc":

            return queryset.order_by("-orders_sum")
        return queryset


class OrderInline(TabularInlinePaginated):
    model = Order
    extra = 0
    max_num = 0
    per_page = 20
    ordering = ["-id"]
    fields = ("number", "payment_amount", "products", "created_at")
    readonly_fields = ("number", "payment_amount", "products", "created_at")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "phone_number",
        "first_name",
        "last_name",
        "patronymic_name",
        "email",
        "display_orders_count",
        "display_orders_sum",
    )
    search_fields = ("email", "phone_number")
    empty_value_display = "-пусто-"
    list_filter = [
        OrderCountFilter,
        OrderSumFilter,
    ]
    inlines = [
        OrderInline,
    ]
    readonly_fields = ("display_orders_count", "display_orders_sum")
    exclude = (
        "username",
        "is_staff",
        "is_active",
        "date_joined",
        "user_permissions",
        "is_superuser",
        "groups",
        "last_login",
        "password",
    )

    def display_orders_count(self, obj):
        return obj.orders.count()

    def display_orders_sum(self, obj):
        old_sum_orders = obj.sum_old_orders if obj.sum_old_orders else 0
        return sum([o.payment_amount for o in obj.orders.all()]) + old_sum_orders

    display_orders_count.short_description = "Кол-во заказов"
    display_orders_sum.short_description = "Сумма заказов"
