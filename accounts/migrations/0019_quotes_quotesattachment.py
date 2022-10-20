# Generated by Django 3.2.13 on 2022-09-12 16:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_delete_recentlyviewed'),
        ('accounts', '0018_auto_20220908_1814'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quotes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.IntegerField()),
                ('quote', models.TextField(blank=True)),
                ('product_fielded_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.product')),
                ('seller', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='QuotesAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_type', models.CharField(choices=[('Image', 'Image'), ('Video', 'Video')], default='Image', max_length=200)),
                ('file', models.FileField(null=True, upload_to='quotes_attachments/%Y/%m/%d/')),
                ('quote', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='accounts.quotes')),
            ],
        ),
    ]
