# Generated by Django 3.2.13 on 2022-09-08 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_auto_20220908_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcountviews',
            name='user',
            field=models.IntegerField(null=True),
        ),
    ]