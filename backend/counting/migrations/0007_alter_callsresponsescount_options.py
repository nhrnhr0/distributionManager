# Generated by Django 4.2 on 2024-11-07 13:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('counting', '0006_alter_telegramgroupsizecount_count'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='callsresponsescount',
            options={'ordering': ['-date'], 'verbose_name': 'Calls Responses Count', 'verbose_name_plural': 'Calls Responses Counts'},
        ),
    ]