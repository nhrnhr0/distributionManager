# Generated by Django 5.1.1 on 2024-11-07 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('counting', '0007_alter_callsresponsescount_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='messagesresponsescount',
            options={'ordering': ['-date'], 'verbose_name': 'Messages Responses Count', 'verbose_name_plural': 'Messages Responses Counts'},
        ),
    ]
