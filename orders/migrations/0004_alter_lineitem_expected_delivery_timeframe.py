# Generated by Django 3.2.13 on 2022-09-09 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_lineitem_ordertracking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lineitem',
            name='expected_delivery_timeframe',
            field=models.CharField(default='', max_length=500),
        ),
    ]
