# Generated by Django 4.2 on 2024-11-03 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0026_category_is_main_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagecategory',
            name='send_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='send at'),
        ),
    ]
