# Generated by Django 4.2 on 2024-09-26 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0025_alter_category_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='footer_image',
            field=models.ImageField(blank=True, null=True, upload_to='businesses/'),
        ),
    ]
