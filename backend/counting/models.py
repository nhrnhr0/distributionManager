from django.db import models
from models.models import WhatsappGroup, Business, TelegramGroup
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.

class DaylyGroupSizeCount(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, verbose_name=_("Business"))
    date = models.DateTimeField(default=timezone.now, verbose_name=_("Date"))

    class Meta:
        verbose_name = _("Dayly Group Size Count")
        verbose_name_plural = _("Dayly Group Size Counts")


class WhatsappGroupSizeCount(models.Model):
    group = models.ForeignKey(WhatsappGroup, on_delete=models.CASCADE, verbose_name=_("Whatsapp Group"))
    count = models.IntegerField(verbose_name=_("Count"))
    session = models.ForeignKey(DaylyGroupSizeCount, on_delete=models.CASCADE, verbose_name=_("Session"), related_name='whatsappgroupsizecount_set')

    def __str__(self):
        return f'{self.group.name} - {self.count}'

    class Meta:
        verbose_name = _("Whatsapp Group Size Count")
        verbose_name_plural = _("Whatsapp Group Size Counts")


class TelegramGroupSizeCount(models.Model):
    group = models.ForeignKey(TelegramGroup, on_delete=models.CASCADE, verbose_name=_("Telegram Group"))
    count = models.IntegerField(verbose_name=_("Count"))
    session = models.ForeignKey(DaylyGroupSizeCount, on_delete=models.CASCADE, verbose_name=_("Session"), related_name='telegramgroupsizecount_set')

    def __str__(self):
        return f'{self.group.name} - {self.count}'

    class Meta:
        verbose_name = _("Telegram Group Size Count")
        verbose_name_plural = _("Telegram Group Size Counts")


class MessagesResponsesCount(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, verbose_name=_("Business"))
    date = models.DateField(default=timezone.now, verbose_name=_("Date"))
    count = models.IntegerField(verbose_name=_("Count"))

    def __str__(self):
        return f'{self.business} - {self.count}'

    class Meta:
        verbose_name = _("Messages Responses Count")
        verbose_name_plural = _("Messages Responses Counts")





class CallsResponsesCount(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, verbose_name=_("Business"))
    date = models.DateField(default=timezone.now, verbose_name=_("Date"))
    count = models.IntegerField(verbose_name=_("Count"))

    def __str__(self):
        return f'{self.business} - {self.count}'

    class Meta:
        verbose_name = _("Calls Responses Count")
        verbose_name_plural = _("Calls Responses Counts")
