# Generated by Django 3.2.13 on 2022-08-15 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_business_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='account_manager_phone_1',
            field=models.CharField(blank=True, default='None', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='company_address_1',
            field=models.CharField(blank=True, default='None', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='company_mailing_address',
            field=models.CharField(blank=True, default='None', max_length=100, null=True),
        ),
    ]
