# Generated by Django 3.0.6 on 2020-11-20 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0022_order_tracking_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(blank=True, default='N/A', max_length=32, null=True),
        ),
    ]
