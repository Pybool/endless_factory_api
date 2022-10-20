# Generated by Django 3.2.13 on 2022-08-19 04:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20220815_0945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='current_stock',
            field=models.IntegerField(default=99, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='initial_stock',
            field=models.IntegerField(default=100, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]