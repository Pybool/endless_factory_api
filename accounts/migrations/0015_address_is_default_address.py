# Generated by Django 3.2.13 on 2022-08-23 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_user_otp_expires_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='is_default_address',
            field=models.BooleanField(default=False),
        ),
    ]