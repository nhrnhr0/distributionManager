# Generated by Django 4.2 on 2024-09-26 07:42

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('counting', '0002_remove_weeklymessagesresponsescount_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklymessagesresponsescount',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
