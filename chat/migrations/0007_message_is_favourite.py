# Generated by Django 3.2.13 on 2022-07-23 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_message_attached_media_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_favourite',
            field=models.BooleanField(default=False),
        ),
    ]