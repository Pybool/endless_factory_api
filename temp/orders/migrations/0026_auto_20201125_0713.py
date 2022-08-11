# Generated by Django 3.0.6 on 2020-11-25 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0025_cartitem_option_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineitem',
            name='option_type',
            field=models.CharField(default='N/A', max_length=100),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='option_value',
            field=models.CharField(default='N/A', max_length=100),
        ),
    ]
