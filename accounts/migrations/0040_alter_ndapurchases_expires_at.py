# Generated by Django 3.2.13 on 2022-10-07 17:27

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0039_alter_ndapurchases_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ndapurchases',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 14, 17, 27, 9, 598306, tzinfo=utc)),
        ),
    ]