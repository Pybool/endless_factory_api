# Generated by Django 3.2.13 on 2022-10-01 19:29

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_rename_complain_reportseller_complaint'),
    ]

    operations = [
        migrations.CreateModel(
            name='NDA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nda_title', models.CharField(default='Generic NDA', max_length=300)),
                ('created_at', models.DateTimeField(verbose_name=datetime.datetime(2022, 10, 1, 19, 29, 4, 989386, tzinfo=utc))),
                ('updated_at', models.DateTimeField(verbose_name=datetime.datetime(2022, 10, 1, 19, 29, 4, 989404, tzinfo=utc))),
            ],
        ),
        migrations.AlterField(
            model_name='address',
            name='created_at',
            field=models.DateTimeField(verbose_name=datetime.datetime(2022, 10, 1, 19, 29, 4, 984923, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='address',
            name='updated_at',
            field=models.DateTimeField(verbose_name=datetime.datetime(2022, 10, 1, 19, 29, 4, 984953, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='review',
            name='created_at',
            field=models.DateTimeField(verbose_name=datetime.datetime(2022, 10, 1, 19, 29, 4, 987704, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='review',
            name='updated_at',
            field=models.DateTimeField(verbose_name=datetime.datetime(2022, 10, 1, 19, 29, 4, 987725, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(verbose_name=datetime.datetime(2022, 10, 1, 19, 29, 4, 982051, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='user',
            name='otp_expires_at',
            field=models.DateTimeField(verbose_name=datetime.datetime(2022, 10, 1, 19, 29, 4, 982004, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(verbose_name=datetime.datetime(2022, 10, 1, 19, 29, 4, 982063, tzinfo=utc)),
        ),
    ]
