from django.test import TestCase
from apps.products.models import Pattern

class PatternModelTest(TestCase):

    def setUp(self):
        """Подготовка данных"""

        self.pattern_data = {
            "article": 12345,
            "name": "Тестовая Выкройка",
            "description": "Тестовое описание",
            "price": 1000
        }
        self.pattern = Pattern.objects.create(**self.pattern_data)

    def test_create_pattern(self):
        """Проверка создания товара"""

        self.assertEqual(self.pattern.article, 12345)
        self.assertEqual(self.pattern.name, "Тестовая Выкройка")
        self.assertEqual(self.pattern.description, "Тестовое описание")
        self.assertEqual(self.pattern.price, 1000)

    def test_str_method(self):
        """Проверка str метода"""

        self.assertEqual(str(self.pattern), "Тестовая Выкройка")

    def test_meta_options(self):
        """Проверка мета полей"""

        self.assertEqual(self.pattern._meta.verbose_name, "Выкройка")
        self.assertEqual(self.pattern._meta.verbose_name_plural, "Выкройки")
