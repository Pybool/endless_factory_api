# Generated by Django 3.2.13 on 2022-09-25 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('careers', '0009_alter_applications_company'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applications',
            name='applicant',
        ),
        migrations.RemoveField(
            model_name='applications',
            name='company',
        ),
        migrations.RemoveField(
            model_name='applications',
            name='job',
        ),
        migrations.DeleteModel(
            name='ApplicantsResume',
        ),
        migrations.DeleteModel(
            name='Applications',
        ),
    ]
