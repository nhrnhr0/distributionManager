# Generated by Django 4.2 on 2024-11-09 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0039_remove_business_ai_message_correction'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoriesclicks',
            name='referrer',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='referrer'),
        ),
        migrations.AddField(
            model_name='leadsclicks',
            name='referrer',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='referrer'),
        ),
        migrations.AddField(
            model_name='messagelinkclick',
            name='referrer',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='referrer'),
        ),
    ]
