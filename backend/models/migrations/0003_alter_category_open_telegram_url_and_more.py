# Generated by Django 5.0.2 on 2024-02-29 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0002_alter_business_slug_alter_category_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='open_telegram_url',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='open_whatsapp_url',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
