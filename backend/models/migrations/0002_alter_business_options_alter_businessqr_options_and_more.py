# Generated by Django 4.2 on 2024-09-26 11:54

import core.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('models', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='business',
            options={'verbose_name': 'business', 'verbose_name_plural': 'businesses'},
        ),
        migrations.AlterModelOptions(
            name='businessqr',
            options={'verbose_name': 'business QR', 'verbose_name_plural': 'business QRs'},
        ),
        migrations.AlterModelOptions(
            name='businessqrcategories',
            options={'verbose_name': 'business QR category', 'verbose_name_plural': 'business QR categories'},
        ),
        migrations.AlterModelOptions(
            name='categoriesclicks',
            options={'verbose_name': 'categories click', 'verbose_name_plural': 'categories clicks'},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'category', 'verbose_name_plural': 'categories'},
        ),
        migrations.AlterModelOptions(
            name='contentschedule',
            options={'ordering': ['-send_date', '-created_at'], 'verbose_name': 'content schedule', 'verbose_name_plural': 'content schedules'},
        ),
        migrations.AlterModelOptions(
            name='leadsclicks',
            options={'verbose_name': 'leads click', 'verbose_name_plural': 'leads clicks'},
        ),
        migrations.AlterModelOptions(
            name='telegramgroup',
            options={'verbose_name': 'Telegram group', 'verbose_name_plural': 'Telegram groups'},
        ),
        migrations.AlterModelOptions(
            name='whatsappgroup',
            options={'verbose_name': 'WhatsApp group', 'verbose_name_plural': 'WhatsApp groups'},
        ),
        migrations.AlterField(
            model_name='business',
            name='description',
            field=models.TextField(blank=True, max_length=20000, null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='business',
            name='footer_image',
            field=models.ImageField(blank=True, null=True, upload_to='businesses/', verbose_name='footer image'),
        ),
        migrations.AlterField(
            model_name='business',
            name='header_image',
            field=models.ImageField(blank=True, null=True, upload_to='businesses/', verbose_name='header image'),
        ),
        migrations.AlterField(
            model_name='business',
            name='name',
            field=models.CharField(max_length=100, verbose_name='שם'),
        ),
        migrations.AlterField(
            model_name='business',
            name='slug',
            field=models.SlugField(allow_unicode=True, max_length=100, unique=True, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='businessqr',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qrs', to='models.business', verbose_name='business'),
        ),
        migrations.AlterField(
            model_name='businessqr',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qrs', to='models.businessqrcategories', verbose_name='category'),
        ),
        migrations.AlterField(
            model_name='businessqr',
            name='name',
            field=models.CharField(max_length=100, verbose_name='שם'),
        ),
        migrations.AlterField(
            model_name='businessqr',
            name='qr_code',
            field=models.CharField(default=core.utils.generate_small_uuid, editable=False, max_length=100, unique=True, verbose_name='QR code'),
        ),
        migrations.AlterField(
            model_name='businessqr',
            name='qr_img',
            field=models.ImageField(blank=True, null=True, upload_to='qrs/', verbose_name='QR image'),
        ),
        migrations.AlterField(
            model_name='businessqrcategories',
            name='name',
            field=models.CharField(max_length=100, verbose_name='שם'),
        ),
        migrations.AlterField(
            model_name='categoriesclicks',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories_clicks', to='models.business', verbose_name='business'),
        ),
        migrations.AlterField(
            model_name='categoriesclicks',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories_clicks', to='models.category', verbose_name='category'),
        ),
        migrations.AlterField(
            model_name='categoriesclicks',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='categoriesclicks',
            name='group_type',
            field=models.CharField(choices=[('whatsapp', 'whatsapp'), ('telegram', 'telegram')], default='whatsapp', max_length=100, verbose_name='group type'),
        ),
        migrations.AlterField(
            model_name='categoriesclicks',
            name='qr',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categories_clicks', to='models.businessqr', verbose_name='QR'),
        ),
        migrations.AlterField(
            model_name='category',
            name='all_telegram_urls',
            field=models.ManyToManyField(related_name='all_telegram_categories', to='models.telegramgroup', verbose_name='all Telegram URLs'),
        ),
        migrations.AlterField(
            model_name='category',
            name='all_whatsapp_urls',
            field=models.ManyToManyField(related_name='all_whatsapp_categories', to='models.whatsappgroup', verbose_name='all WhatsApp URLs'),
        ),
        migrations.AlterField(
            model_name='category',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='models.business', verbose_name='business'),
        ),
        migrations.AlterField(
            model_name='category',
            name='icon',
            field=models.ImageField(blank=True, null=True, upload_to='categories/', verbose_name='icon'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, verbose_name='שם'),
        ),
        migrations.AlterField(
            model_name='category',
            name='open_telegram_url',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='open_telegram_categories', to='models.telegramgroup', verbose_name='open Telegram URL'),
        ),
        migrations.AlterField(
            model_name='category',
            name='open_whatsapp_url',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='open_whatsapp_categories', to='models.whatsappgroup', verbose_name='open WhatsApp URL'),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(allow_unicode=True, max_length=100, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='contentschedule',
            name='approve_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='approve date'),
        ),
        migrations.AlterField(
            model_name='contentschedule',
            name='approve_state',
            field=models.CharField(choices=[('A', 'Approved'), ('P', 'Pending'), ('R', 'Rejected')], default='P', max_length=1, verbose_name='approve state'),
        ),
        migrations.AlterField(
            model_name='contentschedule',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contentSchedules', to='models.business', verbose_name='business'),
        ),
        migrations.AlterField(
            model_name='contentschedule',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='contentSchedules', to='models.category', verbose_name='categories'),
        ),
        migrations.AlterField(
            model_name='contentschedule',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='contentschedule',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='contentschedule',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='contents/', verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='contentschedule',
            name='is_telegram_sent',
            field=models.BooleanField(default=False, verbose_name='is Telegram sent'),
        ),
        migrations.AlterField(
            model_name='contentschedule',
            name='is_whatsapp_sent',
            field=models.BooleanField(default=False, verbose_name='is WhatsApp sent'),
        ),
        migrations.AlterField(
            model_name='contentschedule',
            name='message',
            field=models.TextField(blank=True, max_length=200, null=True, verbose_name='message'),
        ),
        migrations.AlterField(
            model_name='contentschedule',
            name='send_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='send date'),
        ),
        migrations.AlterField(
            model_name='contentschedule',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='updated at'),
        ),
        migrations.AlterField(
            model_name='leadsclicks',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leads_clicks', to='models.business', verbose_name='business'),
        ),
        migrations.AlterField(
            model_name='leadsclicks',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='leadsclicks',
            name='qr',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='leads_clicks', to='models.businessqr', verbose_name='QR'),
        ),
        migrations.AlterField(
            model_name='sysuser',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='models.business', verbose_name='business'),
        ),
        migrations.AlterField(
            model_name='sysuser',
            name='name',
            field=models.CharField(max_length=100, verbose_name='שם'),
        ),
        migrations.AlterField(
            model_name='sysuser',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='me', to=settings.AUTH_USER_MODEL, verbose_name='משתמש'),
        ),
        migrations.AlterField(
            model_name='telegramgroup',
            name='chat_id',
            field=models.CharField(max_length=120, verbose_name='chat ID'),
        ),
        migrations.AlterField(
            model_name='telegramgroup',
            name='last_members_check',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last members check'),
        ),
        migrations.AlterField(
            model_name='telegramgroup',
            name='last_members_count',
            field=models.PositiveIntegerField(default=0, verbose_name='last members count'),
        ),
        migrations.AlterField(
            model_name='telegramgroup',
            name='name',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='שם'),
        ),
        migrations.AlterField(
            model_name='whatsappgroup',
            name='chat_id',
            field=models.CharField(max_length=120, verbose_name='chat ID'),
        ),
        migrations.AlterField(
            model_name='whatsappgroup',
            name='last_members_check',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last members check'),
        ),
        migrations.AlterField(
            model_name='whatsappgroup',
            name='last_members_count',
            field=models.PositiveIntegerField(default=0, verbose_name='last members count'),
        ),
        migrations.AlterField(
            model_name='whatsappgroup',
            name='name',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='שם'),
        ),
    ]
