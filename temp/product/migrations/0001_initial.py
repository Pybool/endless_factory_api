# Generated by Django 3.0.6 on 2020-05-31 22:05

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('color', models.CharField(max_length=50)),
                ('model_number', models.CharField(max_length=100)),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('min_order_quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('max_order_quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('pickup_available', models.BooleanField(default=False)),
                ('delivery_available', models.BooleanField(default=False)),
                ('pricing_option', models.CharField(max_length=200)),
                ('product_type', models.CharField(max_length=200)),
                ('payment_plan_acceptance_option', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductAttachments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_type', models.CharField(max_length=200)),
                ('image', models.ImageField(blank=True, null=True, upload_to='product_attachments')),
                ('product', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='product.Product')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='search_tags',
            field=models.ManyToManyField(to='product.Tag'),
        ),
    ]