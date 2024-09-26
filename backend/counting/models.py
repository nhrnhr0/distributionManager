from django.db import models
from models.models import WhatsappGroup,Business, TelegramGroup
from django.utils import timezone
# Create your models here.


class DaylyGroupSizeCount(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,editable=True)


class WhatsappGroupSizeCount(models.Model):
    group = models.ForeignKey(WhatsappGroup, on_delete=models.CASCADE)
    count = models.IntegerField()
    session = models.ForeignKey(DaylyGroupSizeCount, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.group_size} - {self.count}'
    
class TelegramGroupSizeCount(models.Model):
    group = models.ForeignKey(TelegramGroup, on_delete=models.CASCADE)
    count = models.IntegerField()
    session = models.ForeignKey(DaylyGroupSizeCount, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.group_size} - {self.count}'
    
    
class WeeklyMessagesResponsesCount(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    count = models.IntegerField()
    def __str__(self):
        return f'{self.business} - {self.count}'

