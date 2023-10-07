from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

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
