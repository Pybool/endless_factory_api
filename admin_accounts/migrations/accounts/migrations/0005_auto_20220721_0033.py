# Generated by Django 3.2.13 on 2022-07-21 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20220721_0031'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='account_manager_name',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name='user',
            name='account_manager_phone_1',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='user',
            name='account_manager_phone_2',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='user',
            name='ceo_id_card',
            field=models.FileField(null=True, upload_to='id_cards_attachments'),
        ),
        migrations.AddField(
            model_name='user',
            name='city_location',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name='user',
            name='company_address_1',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='user',
            name='company_address_2',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='user',
            name='company_ceo_name',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name='user',
            name='company_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='company_mailing_address',
            field=models.EmailField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='company_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='user',
            name='company_postal_code',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name='user',
            name='contact_preferences',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='has_existing_shop',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='proof_of_business',
            field=models.FileField(null=True, upload_to='business_ownership_attachments'),
        ),
        migrations.AddField(
            model_name='user',
            name='referrer_email',
            field=models.EmailField(blank=True, max_length=255, null=True, verbose_name='email address'),
        ),
        migrations.AddField(
            model_name='user',
            name='store_name',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]