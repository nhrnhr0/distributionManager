# Generated by Django 4.2 on 2024-09-25 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0016_remove_business_qrs_businessqr_business'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='businessqr',
            name='image',
        ),
    ]
