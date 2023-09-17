from django.contrib import admin
from django.utils.html import format_html

from .models import Pattern


@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "display_image",
    )
    search_fields = (
        "article",
        "price",
    )
    list_filter = ("price", "name")
    empty_value_display = "-пусто-"

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="170" height="220" />', obj.image.url)
        return None

    display_image.short_description = "Мини-изображение"
