# Generated by Django 4.2 on 2024-11-07 23:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0037_remove_category_ai_message_example_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='business',
            old_name='ai_message_prompt',
            new_name='ai_system_prompt',
        ),
    ]
