# Generated by Django 3.0.6 on 2020-08-02 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0013_auto_20200726_0945'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='stripe_transaction_id',
            field=models.CharField(default='stripe_transaction_ref', editable=False, max_length=100),
        ),
    ]