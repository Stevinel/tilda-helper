from django.contrib import admin
from django_admin_inline_paginator.admin import TabularInlinePaginated

from ..orders.models import Order
from .models import Customer


class OrderCountFilter(admin.SimpleListFilter):
    title = "Кол-во заказов"
    parameter_name = "order_count"

    def lookups(self, request, model_admin):
        return (
            ("asc", "По возрастанию"),
            ("desc", "По убыванию"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "asc":
            return queryset.order_by("orders_count")
        elif value == "desc":
            return queryset.order_by("-orders_count")
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
    )
    search_fields = ("email", "phone_number")
    empty_value_display = "-пусто-"
    list_filter = [
        OrderCountFilter,
    ]
    inlines = [
        OrderInline,
    ]
    readonly_fields = ("display_orders_count",)
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
        return obj.orders_count

    display_orders_count.short_description = "Кол-во заказов"
