# Generated by Django 4.2 on 2024-10-07 22:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0016_alter_messagelink_uid'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageLinkClick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='נוצר ב')),
                ('group_type', models.CharField(choices=[('whatsapp', 'whatsapp'), ('telegram', 'telegram')], default='whatsapp', max_length=100, verbose_name='סוג קבוצה')),
                ('ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP')),
                ('user_agent', models.TextField(blank=True, null=True, verbose_name='user agent')),
                ('link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clicks', to='models.messagelink', verbose_name='link')),
                ('msg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clicks', to='models.bizmessages', verbose_name='הודעה')),
            ],
        ),
    ]