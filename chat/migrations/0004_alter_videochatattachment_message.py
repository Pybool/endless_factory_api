# Generated by Django 3.2.13 on 2022-07-22 07:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_auto_20220722_0046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videochatattachment',
            name='message',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='chat.message'),
        ),
    ]