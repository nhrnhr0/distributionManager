from typing import Iterable
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
import backend.settings as settings
import requests
import uuid

class SysUser(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='me')
    business = models.ForeignKey('Business', on_delete=models.CASCADE, related_name='users')
    def __str__(self) -> str:
        return self.name

class Business(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True)
    
    
    header_image = models.ImageField(upload_to='businesses/', blank=True, null=True)
    description = models.TextField(max_length=200, blank=True, null=True)

    def __str__(self) -> str:
        return self.name
    
    def get_absolute_url(self):
        return '/join/' + self.slug

class WhatsappGroup(models.Model):
    name = models.CharField(max_length=120,blank=True,null=True)
    chat_id = models.CharField(max_length=120)
    last_members_count = models.PositiveIntegerField(default=0)
    last_members_check = models.DateTimeField(blank=True,null=True)

    def get_link(self):
        return 'https://chat.whatsapp.com/' + self.chat_id
    
    def save(self):
        print(self.chat_id)
        if self.chat_id.startswith('https://chat.whatsapp.com/'):
            self.chat_id = self.chat_id.replace('https://chat.whatsapp.com/', '')
        return super().save()
    def __str__(self) -> str:
        return self.name +' - (' +  (''.join([c.name for c in self.all_whatsapp_categories.all()])) + ')'
    

class TelegramGroup(models.Model):
    name = models.CharField(max_length=120,blank=True,null=True)
    chat_id= models.CharField(max_length=120)
    last_members_count = models.PositiveIntegerField(default=0)
    last_members_check = models.DateTimeField(blank=True,null=True)

    def get_link(self):
        return 'https://t.me/' + self.chat_id
    
    def save(self):
        if self.chat_id.startswith('https://t.me/'):
            self.chat_id = self.chat_id.replace('https://t.me/', '')
        return super().save()
    
    def __str__(self) -> str:
        return self.name +' - (' +  (''.join([c.name for c in self.all_telegram_categories.all()])) + ')'
    
    
    
class Category(models.Model):
    icon = models.ImageField(upload_to='categories/', blank=True, null=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100,allow_unicode=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='categories')
    open_whatsapp_url = models.ForeignKey(to=WhatsappGroup, on_delete=models.SET_NULL, related_name='open_whatsapp_categories', null=True, blank=True)
    open_telegram_url = models.ForeignKey(to=TelegramGroup, on_delete=models.SET_NULL, related_name='open_telegram_categories', null=True, blank=True)
    
    all_whatsapp_urls = models.ManyToManyField(to=WhatsappGroup, related_name='all_whatsapp_categories')
    all_telegram_urls = models.ManyToManyField(to=TelegramGroup, related_name='all_telegram_categories')
    
    def __str__(self) -> str:
        return self.name + ' - ' + self.business.name
    
    class Meta:
        unique_together = ('name', 'business')
        
    def save(self):
        return super().save()

    def image_display(self):
        if self.icon:
            return mark_safe(f'<img src="{self.icon.url}" width="50" height="50" />')
        return 'No Image'
    
    def send_telegram_message(self, message: 'ContentSchedule'):
        
        chat_ids = self.all_telegram_urls
        text = message.message
        for chat_id in chat_ids.values_list('chat_id', flat=True):
            if chat_id:
                if message.image:
                    telegram_url = f"https://api.telegram.org/bot{settings.env.str('TELEGRAM_BOT_TOKEN')}/sendPhoto"
                    img_url = f'{message.image.url}'
                    
                    payload = {
                        'chat_id': '@' + chat_id,
                        'photo': img_url,
                        'caption': text
                    }
                    response = requests.post(telegram_url, json=payload)
                    
                else:
                    telegram_url = f"https://api.telegram.org/bot{settings.env.str('TELEGRAM_BOT_TOKEN')}/sendMessage"
                    payload = {
                        'chat_id': '@' + chat_id,
                        'text': text
                    }
                    response = requests.post(telegram_url, json=payload)
                if response.status_code == 200: 
                    print("Telegram message sent successfully")
                    print(response.text)
                else:
                    print(response.text)
                    print("Failed to send Telegram message")
        
@receiver(post_save, sender=Category, dispatch_uid="update_open_groups")
def update_open_groups(sender, instance, **kwargs):
    updated = False
    if instance.open_whatsapp_url:
        if not instance.all_whatsapp_urls.filter(id=instance.open_whatsapp_url.id).exists():
            instance.all_whatsapp_urls.add(instance.open_whatsapp_url)
            updated = True
    else:
        instance.open_whatsapp_url = instance.all_whatsapp_urls.first()
        if instance.open_whatsapp_url:
            updated = True
    
    if instance.open_telegram_url:
        if not instance.all_telegram_urls.filter(id=instance.open_telegram_url.id).exists():
            instance.all_telegram_urls.add(instance.open_telegram_url)
            updated = True
    else:
        instance.open_telegram_url = instance.all_telegram_urls.first()
        if instance.open_telegram_url:
            updated = True
    if updated:
        instance.save()

# content state options: Approved, Pending, Rejected
CONTENT_STATE = (
    ('A', 'Approved'),
    ('P', 'Pending'),
    ('R', 'Rejected'),
)

class ContentSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='contents/', blank=True, null=True)
    send_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='contentSchedules')

    approve_state = models.CharField(max_length=1, choices=CONTENT_STATE, default='P')
    approve_date = models.DateTimeField(blank=True, null=True)
    # reject_reason = models.TextField(max_length=200, blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='contentSchedules', blank=True)
    
    is_whatsapp_sent = models.BooleanField(default=False)
    is_telegram_sent = models.BooleanField(default=False)
    
    def send_telgram_message(self):
        for cat in self.categories.all():
            cat.send_telegram_message(self)
        self.is_telegram_sent = True
        self.save()
    
    def should_send_whatsapp(self):
        if self.is_whatsapp_sent:
            return False
        if self.approve_state != 'A':
            return False
        
        if self.send_date and self.send_date <= timezone.now():
            return True
    
        return False
    def should_send_telegram(self):
        if self.is_telegram_sent:
            return False
        if self.approve_state != 'A':
            return False
        # if updated_at happend in the last 5 minutes
        if self.updated_at and (timezone.now() - self.updated_at).seconds < 300:
            return False
        if self.send_date and self.send_date <= timezone.now():
            return True
        return False
    class Meta:
        ordering = ['-send_date', '-created_at']