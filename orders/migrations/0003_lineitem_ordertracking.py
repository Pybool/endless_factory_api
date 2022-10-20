# Generated by Django 3.2.13 on 2022-09-09 16:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order_tracking', '0001_initial'),
        ('orders', '0002_alter_lineitem_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineitem',
            name='ordertracking',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='order_tracking.ordertracking'),
        ),
    ]
