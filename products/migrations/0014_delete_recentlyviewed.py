# Generated by Django 3.2.13 on 2022-09-12 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_recentlyviewed'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RecentlyViewed',
        ),
    ]
