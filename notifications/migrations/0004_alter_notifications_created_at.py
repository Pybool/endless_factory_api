# Generated by Django 3.2.13 on 2022-09-13 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_notifications_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifications',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]