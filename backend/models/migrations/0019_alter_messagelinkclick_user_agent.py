# Generated by Django 4.2 on 2024-10-08 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0018_messagelinkclick_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagelinkclick',
            name='user_agent',
            field=models.TextField(blank=True, null=True, verbose_name='דפדפן'),
        ),
    ]