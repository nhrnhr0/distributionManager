# Generated by Django 5.0.2 on 2024-03-04 10:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0006_contentschedule_is_sent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='business',
            name='users',
        ),
        migrations.AddField(
            model_name='sysuser',
            name='business',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='models.business'),
            preserve_default=False,
        ),
    ]
