# Generated by Django 3.1.5 on 2021-06-07 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_auto_20201125_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]
