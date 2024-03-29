# Generated by Django 5.0.2 on 2024-03-05 11:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0008_alter_sysuser_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(max_length=120)),
                ('last_members_count', models.PositiveIntegerField(default=0)),
                ('last_members_check', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='WhatsappGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(max_length=120)),
                ('last_members_count', models.PositiveIntegerField(default=0)),
                ('last_members_check', models.DateTimeField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='contentschedule',
            options={'ordering': ['-send_date', '-created_at']},
        ),
        migrations.RemoveField(
            model_name='contentschedule',
            name='reject_reason',
        ),
        migrations.RemoveField(
            model_name='category',
            name='all_telegram_urls',
        ),
        migrations.RemoveField(
            model_name='category',
            name='all_whatsapp_urls',
        ),
        migrations.AlterField(
            model_name='category',
            name='open_telegram_url',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='open_telegram_categories', to='models.telegramgroup'),
        ),
        migrations.AlterField(
            model_name='category',
            name='open_whatsapp_url',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='open_whatsapp_categories', to='models.whatsappgroup'),
        ),
        migrations.AddField(
            model_name='category',
            name='all_telegram_urls',
            field=models.ManyToManyField(related_name='all_telegram_categories', to='models.telegramgroup'),
        ),
        migrations.AddField(
            model_name='category',
            name='all_whatsapp_urls',
            field=models.ManyToManyField(related_name='all_whatsapp_categories', to='models.whatsappgroup'),
        ),
    ]
