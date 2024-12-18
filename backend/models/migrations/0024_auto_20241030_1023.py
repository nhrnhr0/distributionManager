# Generated by Django 4.2 on 2024-10-30 08:23

from django.db import migrations

def init_businessqr_order(apps, schema_editor):
    BusinessQR = apps.get_model('models', 'BusinessQR')
    for i, c in enumerate(BusinessQR.objects.all()):
        c.the_order = i
        c.save()
        

class Migration(migrations.Migration):

    dependencies = [
        ('models', '0023_alter_businessqr_options_businessqr_the_order'),
    ]

    operations = [
        migrations.RunPython(init_businessqr_order),
    ]
