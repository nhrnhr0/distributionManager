# Generated by Django 5.1.1 on 2024-10-30 22:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0024_auto_20241030_1023'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telegramgroup',
            name='last_members_check',
        ),
        migrations.RemoveField(
            model_name='telegramgroup',
            name='last_members_count',
        ),
        migrations.RemoveField(
            model_name='whatsappgroup',
            name='last_members_check',
        ),
        migrations.RemoveField(
            model_name='whatsappgroup',
            name='last_members_count',
        ),
    ]