from django.db import models
from django.db.models import CharField, DateTimeField, FileField, ImageField, PositiveIntegerField


class Product(models.Model):
    """Абстрактная модель товара"""

    article = PositiveIntegerField("Артикул", blank=False, db_index=True)
    name = CharField("Название", max_length=256)
    description = CharField("Краткое описание", blank=True)
    price = PositiveIntegerField("Цена")
    created_at = DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        abstract = True


class Pattern(Product):
    """Модель выкроек"""

    pdf_file = FileField("PDF файл", upload_to="pattern/pdfs/", blank=True)
    image = ImageField("Изображение товара", upload_to="pattern/images/", blank=True)

    class Meta:
        verbose_name = "Выкройка"
        verbose_name_plural = "Выкройки"

    def __str__(self):
        return self.name
