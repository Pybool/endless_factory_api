# Generated by Django 3.2.13 on 2022-08-03 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_resetpassword_otp_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resetpassword',
            name='otp_expires_at',
            field=models.DateTimeField(default='2000-01-01 01:01:30.475275'),
        ),
    ]
