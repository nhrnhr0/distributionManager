# Generated by Django 4.2 on 2024-10-29 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0020_alter_category_options_category_the_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['the_order'], 'verbose_name': 'קטגוריה', 'verbose_name_plural': 'קטגוריות'},
        ),
    ]
# create empty migration
# python manage.py makemigrations --empty models