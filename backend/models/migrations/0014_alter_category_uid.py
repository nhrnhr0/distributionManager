# Generated by Django 4.2 on 2024-10-07 21:55

import core.utils
from django.db import migrations, models

def generate_uuid_for_existing_categories(apps, schema_editor):
    Category = apps.get_model('models', 'Category')
    for category in Category.objects.all():
        category.uid = core.utils.generate_small_uuid()
        category.save()
        

class Migration(migrations.Migration):

    dependencies = [
        ('models', '0013_category_uid'),
    ]

    operations = [
        migrations.RunPython(generate_uuid_for_existing_categories),
        migrations.AlterField(
            model_name='category',
            name='uid',
            field=models.CharField(default=core.utils.generate_small_uuid, editable=False, max_length=100, unique=True, verbose_name='uid'),
        ),
    ]