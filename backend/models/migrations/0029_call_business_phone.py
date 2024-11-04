# Generated by Django 4.2 on 2024-11-03 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0028_alter_bizmessages_uid_alter_category_uid_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Call',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caller_id', models.CharField(blank=True, max_length=50, null=True)),
                ('call_status', models.CharField(blank=True, max_length=50, null=True)),
                ('call_length', models.IntegerField(blank=True, null=True)),
                ('time_started', models.CharField(max_length=50)),
                ('own_number_friendly', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='business',
            name='phone',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='phone'),
        ),
    ]
