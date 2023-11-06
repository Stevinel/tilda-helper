import re

from apps.customers.models import Customer
from django.core.management.base import BaseCommand
from django.db import transaction
from openpyxl import load_workbook

# Признаки для определения покупателя как "мастер"
MASTER_DATA = [
    "100",
    "150",
    "180",
    "250",
    "300",
    "350",
    "мастер",
    "видео",
    "марафон",
    "курс",
    "Я сама",
    "помоги",
    "Мастер-класс",
    "Сама",
    "Видеокурс",
    "Видеоурок",
    "ПОМОГИ",
    "Курс",
    "Марафон"
]

class Command(BaseCommand):
    help = "Парсит древние таблицы с заказами и записывает их в существующую БД"

    def __init__(self):
        super(Command, self).__init__()
        self.master = {}
        self.default_customer = {}

    def handle(self, *args, **kwargs):
        # Загружаем Excel
        workbook = load_workbook(filename='all_data.xlsx')
        sheet = workbook.active

        # Проходим по строкам начиная со второй (исключая заголовки)
        for row in sheet.iter_rows(min_row=2):
            product = row[4].value  # столбец E - products
            email = row[1].value  # столбец B - Email
            name = row[0].value  # столбец A - Name
            price = row[5].value  # столбец F - price
            phone = row[13].value  # столбец N - Phone

            if all([product, price, email]):
                # Проверяем наличие ключевых слов в продукте
                if any(keyword in product for keyword in MASTER_DATA):
                    if email in self.master:
                        self.master[email][2] += round(float(price))
                    else:
                        self.master[email] = [name, phone, round(float(price))]

                # Отдельный словарь с инфой о простых покупателях
                else:
                    if email in self.default_customer:
                        self.default_customer[email][2] += round(float(price))
                    else:
                        self.default_customer[email] = [name, phone, round(float(price))]

        if self.master:
            self.save_customers()

    @staticmethod
    def get_fio(full_name):
        """Разбивка ФИО на части"""

        full_name = full_name.split() if full_name else ""

        last_name = full_name[0] if len(full_name) >= 1 else ""
        first_name = full_name[1] if len(full_name) >= 2 else ""
        patronymic_name = full_name[2] if len(full_name) >= 3 else ""

        return last_name, first_name, patronymic_name

    @staticmethod
    def get_phone(phone):
        """Форматируем номер телефона"""

        if not phone:
            return "+7 (666) 666-66-66"

        digits = re.sub(r'\D', '', phone)

        # Проверяем начало номера и длину
        if len(digits) == 11 and (digits.startswith('7') or digits.startswith('8')):
            # Используем срез для форматирования, отбрасывая первую цифру
            return "+7 ({}) {}-{}-{}".format(digits[1:4], digits[4:7], digits[7:9], digits[9:11])
        elif len(digits) == 10:
            # Если номер уже без ведущей 7 или 8
            return "+7 ({}) {}-{}-{}".format(digits[0:3], digits[3:6], digits[6:8], digits[8:10])
        elif phone == 'yes':
            return "+7 (666) 666-66-66"
        else:
            return phone

    @transaction.atomic
    def save_customers(self):
        """Сохранение клиентов в БД"""

        for email, values in self.master.items():
            last_name, first_name, patronymic_name = self.get_fio(values[0])
            phone = self.get_phone(values[1])
            sum_orders = values[2] if values[2] else 0

            try:
                Customer.objects.get(email=email)
            except Customer.DoesNotExist:
                Customer.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    patronymic_name=patronymic_name,
                    email=email,
                    phone_number=phone,
                    sum_old_orders=sum_orders,
                )
