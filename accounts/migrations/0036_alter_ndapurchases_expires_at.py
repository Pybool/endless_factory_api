# Generated by Django 3.2.13 on 2022-10-03 09:56

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0035_auto_20221003_0009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ndapurchases',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 10, 9, 56, 57, 303164, tzinfo=utc)),
        ),
    ]
