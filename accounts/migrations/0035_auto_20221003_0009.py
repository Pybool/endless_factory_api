# Generated by Django 3.2.13 on 2022-10-03 00:09

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0034_auto_20221002_2352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ndaproposals',
            name='slug',
            field=models.SlugField(default=None, max_length=500),
        ),
        migrations.AlterField(
            model_name='ndapurchases',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 10, 0, 9, 39, 197378, tzinfo=utc)),
        ),
    ]
