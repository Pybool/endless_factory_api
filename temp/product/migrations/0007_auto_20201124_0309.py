# Generated by Django 3.0.6 on 2020-11-24 03:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_auto_20200622_2254'),
    ]

    operations = [
        migrations.CreateModel(
            name='OptionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.CharField(default='N/A', max_length=100),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='OptionValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('option_type', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.OptionType')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='option_type',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.OptionType'),
        ),
    ]
