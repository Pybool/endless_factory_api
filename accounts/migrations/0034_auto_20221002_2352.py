# Generated by Django 3.2.13 on 2022-10-02 23:52

import datetime
import django.core.validators
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0033_auto_20221002_2352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ndapurchases',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 9, 23, 52, 51, 365555, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='ndauser',
            name='nda_bought',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
