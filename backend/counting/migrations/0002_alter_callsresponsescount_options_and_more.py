# Generated by Django 4.2 on 2024-09-30 08:59

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0003_alter_business_options_alter_businessqr_options_and_more'),
        ('counting', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='callsresponsescount',
            options={'verbose_name': 'Calls Responses Count', 'verbose_name_plural': 'Calls Responses Counts'},
        ),
        migrations.AlterModelOptions(
            name='daylygroupsizecount',
            options={'verbose_name': 'Dayly Group Size Count', 'verbose_name_plural': 'Dayly Group Size Counts'},
        ),
        migrations.AlterModelOptions(
            name='messagesresponsescount',
            options={'verbose_name': 'Messages Responses Count', 'verbose_name_plural': 'Messages Responses Counts'},
        ),
        migrations.AlterModelOptions(
            name='telegramgroupsizecount',
            options={'verbose_name': 'Telegram Group Size Count', 'verbose_name_plural': 'Telegram Group Size Counts'},
        ),
        migrations.AlterModelOptions(
            name='whatsappgroupsizecount',
            options={'verbose_name': 'Whatsapp Group Size Count', 'verbose_name_plural': 'Whatsapp Group Size Counts'},
        ),
        migrations.AlterField(
            model_name='callsresponsescount',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='models.business', verbose_name='Business'),
        ),
        migrations.AlterField(
            model_name='callsresponsescount',
            name='count',
            field=models.IntegerField(verbose_name='Count'),
        ),
        migrations.AlterField(
            model_name='callsresponsescount',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='daylygroupsizecount',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='models.business', verbose_name='Business'),
        ),
        migrations.AlterField(
            model_name='daylygroupsizecount',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='messagesresponsescount',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='models.business', verbose_name='Business'),
        ),
        migrations.AlterField(
            model_name='messagesresponsescount',
            name='count',
            field=models.IntegerField(verbose_name='Count'),
        ),
        migrations.AlterField(
            model_name='messagesresponsescount',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='telegramgroupsizecount',
            name='count',
            field=models.IntegerField(verbose_name='Count'),
        ),
        migrations.AlterField(
            model_name='telegramgroupsizecount',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='models.telegramgroup', verbose_name='Telegram Group'),
        ),
        migrations.AlterField(
            model_name='telegramgroupsizecount',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='telegramgroupsizecount_set', to='counting.daylygroupsizecount', verbose_name='Session'),
        ),
        migrations.AlterField(
            model_name='whatsappgroupsizecount',
            name='count',
            field=models.IntegerField(verbose_name='Count'),
        ),
        migrations.AlterField(
            model_name='whatsappgroupsizecount',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='models.whatsappgroup', verbose_name='Whatsapp Group'),
        ),
        migrations.AlterField(
            model_name='whatsappgroupsizecount',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='whatsappgroupsizecount_set', to='counting.daylygroupsizecount', verbose_name='Session'),
        ),
    ]
