# Generated by Django 3.2.13 on 2022-06-09 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_product_featured'),
    ]

    operations = [
        migrations.AlterField(
            model_name='optiontype',
            name='name',
            field=models.CharField(default='opt', max_length=100),
        ),
    ]