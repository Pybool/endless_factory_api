# Generated by Django 3.2.13 on 2022-09-24 06:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('careers', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='type',
            new_name='company_type',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='gender',
            new_name='location',
        ),
    ]
