# Generated by Django 3.0.6 on 2020-08-19 20:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_auto_20200819_1859'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='token',
        ),
    ]
