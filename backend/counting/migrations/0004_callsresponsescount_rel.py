# Generated by Django 4.2 on 2024-11-04 00:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0030_business_telegram_fotter'),
        ('counting', '0003_alter_daylygroupsizecount_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='callsresponsescount',
            name='rel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='models.call', verbose_name='Call'),
        ),
    ]