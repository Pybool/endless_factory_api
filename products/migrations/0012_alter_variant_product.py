# Generated by Django 3.2.13 on 2022-09-09 16:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_variant_initial_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variant',
            name='product',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='products.product'),
        ),
    ]
