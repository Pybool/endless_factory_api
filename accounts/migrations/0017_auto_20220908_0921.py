# Generated by Django 3.2.13 on 2022-09-08 09:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_alter_variant_discount'),
        ('accounts', '0016_address_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlistedproduct',
            name='variant',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.variant'),
        ),
        migrations.AlterField(
            model_name='wishlistedproduct',
            name='product',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.product'),
        ),
        migrations.AlterUniqueTogether(
            name='wishlistedproduct',
            unique_together={('product', 'variant', 'user')},
        ),
    ]
