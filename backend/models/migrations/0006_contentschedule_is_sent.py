# Generated by Django 5.0.2 on 2024-03-04 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0005_business_description_business_header_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentschedule',
            name='is_sent',
            field=models.BooleanField(default=False),
        ),
    ]
