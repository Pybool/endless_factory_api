# Generated by Django 3.2.13 on 2022-09-12 17:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_quotes_quotesattachment'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportSeller',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.IntegerField()),
                ('complain', models.TextField(blank=True)),
                ('radio_text', models.CharField(max_length=300)),
                ('seller', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
