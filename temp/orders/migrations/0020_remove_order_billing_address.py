# Generated by Django 3.0.6 on 2020-09-04 20:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0019_order_is_shipped'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='billing_address',
        ),
    ]
