# Generated by Django 4.2 on 2024-10-01 07:27

import core.utils
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0003_alter_business_options_alter_businessqr_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BizMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='נוצר ב')),
                ('message', models.TextField(max_length=20000, verbose_name='הודעה')),
                ('send_at', models.DateTimeField(blank=True, null=True, verbose_name='send at')),
                ('is_sent', models.BooleanField(default=False, verbose_name='is sent')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='models.business', verbose_name='עסק')),
                ('categories', models.ManyToManyField(related_name='messages', to='models.category', verbose_name='קטגוריות')),
                ('telegram_groups', models.ManyToManyField(related_name='messages', to='models.telegramgroup', verbose_name='telegram groups')),
                ('whatsapp_groups', models.ManyToManyField(related_name='messages', to='models.whatsappgroup', verbose_name='whatsapp groups')),
            ],
        ),
        migrations.CreateModel(
            name='MessageLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField(max_length=2000, verbose_name='link')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='models.bizmessages', verbose_name='הודעה')),
            ],
        ),
        migrations.CreateModel(
            name='MessageLinkClick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='נוצר ב')),
                ('ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP')),
                ('user_agent', models.TextField(blank=True, null=True, verbose_name='user agent')),
                ('referer', models.URLField(blank=True, null=True, verbose_name='referer')),
            ],
        ),
        migrations.CreateModel(
            name='MessageLinkTracker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(default=core.utils.generate_small_uuid, editable=False, max_length=100, unique=True, verbose_name='uid')),
                ('group_type', models.CharField(choices=[('whatsapp', 'whatsapp'), ('telegram', 'telegram')], default='whatsapp', max_length=100, verbose_name='סוג קבוצה')),
                ('link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trackers', to='models.messagelink', verbose_name='link')),
                ('telegram_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trackers', to='models.telegramgroup', verbose_name='קבוצה')),
                ('whatsapp_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trackers', to='models.whatsappgroup', verbose_name='קבוצה')),
            ],
        ),
        migrations.DeleteModel(
            name='ContentSchedule',
        ),
        migrations.AddField(
            model_name='messagelinkclick',
            name='tracker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clicks', to='models.messagelinktracker', verbose_name='tracker'),
        ),
    ]
