# Generated by Django 3.2.13 on 2022-09-24 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careers', '0003_company_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='company_type',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='company',
            name='location',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='company',
            name='phone',
            field=models.CharField(max_length=20),
        ),
    ]
