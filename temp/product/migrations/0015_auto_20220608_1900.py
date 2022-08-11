# Generated by Django 3.2.13 on 2022-06-09 02:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0014_alter_optiontype_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='optiontype',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='product',
            name='option_type',
            field=models.ForeignKey(default='default', null=True, on_delete=django.db.models.deletion.CASCADE, to='product.optiontype'),
        ),
    ]