# Generated by Django 3.0.6 on 2020-11-24 04:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_auto_20201124_0309'),
    ]

    operations = [
        migrations.AddField(
            model_name='variant',
            name='option_value',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.OptionValue'),
        ),
    ]
