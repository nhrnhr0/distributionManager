# Generated by Django 4.2 on 2024-10-30 08:14

from django.db import migrations

def init_categories_order(apps, schema_editor):
    Category = apps.get_model('models', 'Category')
    for i, c in enumerate(Category.objects.all()):
        c.the_order = i
        c.save()
        
class Migration(migrations.Migration):

    dependencies = [
        ('models', '0021_alter_category_options'),
    ]

    operations = [
        migrations.RunPython(init_categories_order),
    ]
