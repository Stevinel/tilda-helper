# Generated by Django 4.2.5 on 2023-11-06 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='sum_old_orders',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Сумма старых заказов из таблиц'),
        ),
    ]
