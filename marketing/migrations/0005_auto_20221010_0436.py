# Generated by Django 3.2.13 on 2022-10-10 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0004_auto_20221007_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='active_cmd',
            field=models.CharField(blank=True, default='system', max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='schedule_cmd',
            field=models.CharField(blank=True, default='system', max_length=150, null=True),
        ),
    ]
