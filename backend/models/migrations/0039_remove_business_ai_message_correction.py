# Generated by Django 4.2 on 2024-11-07 23:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0038_rename_ai_message_prompt_business_ai_system_prompt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='business',
            name='ai_message_correction',
        ),
    ]
