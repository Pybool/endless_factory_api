# Generated by Django 3.2.13 on 2022-09-25 17:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('careers', '0008_auto_20220925_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applications',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='careers.company'),
        ),
    ]
