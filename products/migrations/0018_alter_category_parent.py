# Generated by Django 3.2.13 on 2022-09-13 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_alter_category_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='parent',
            field=models.IntegerField(default=-1, null=True),
        ),
    ]
