# Generated by Django 3.2.13 on 2022-08-24 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_address_is_default_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
