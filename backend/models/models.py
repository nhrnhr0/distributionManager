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
from django.utils.translation import gettext as _
import qrcode
import os
import requests
from io import BytesIO
from django.core.files import File
from core.utils import generate_small_uuid

class SysUser(models.Model):
    name = models.CharField(_('name'), max_length=100)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='me', verbose_name=_('user'))
    business = models.ForeignKey('Business', on_delete=models.CASCADE, related_name='users', verbose_name=_('business'))
    
    def __str__(self) -> str:
        return self.name

class Business(models.Model):
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True, allow_unicode=True)
    header_image = models.ImageField(_('header image'), upload_to='businesses/', blank=True, null=True)
    footer_image = models.ImageField(_('footer image'), upload_to='businesses/', blank=True, null=True)
    description = models.TextField(_('description'), max_length=20000, blank=True, null=True)
    
    def __str__(self) -> str:
        return self.name
    
    def get_absolute_url(self):
        return '/join/' + self.slug

    class Meta:
        verbose_name = _('business')
        verbose_name_plural = _('businesses')

class BusinessQRCategories(models.Model):
    name = models.CharField(_('name'), max_length=100)
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _('business QR category')
        verbose_name_plural = _('business QR categories')

class LeadsClicks(models.Model):
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='leads_clicks', verbose_name=_('business'))
    qr = models.ForeignKey('BusinessQR', on_delete=models.CASCADE, related_name='leads_clicks', null=True, blank=True, verbose_name=_('QR'))
    
    class Meta:
        verbose_name = _('leads click')
        verbose_name_plural = _('leads clicks')

class CategoriesClicks(models.Model):
    CATEGORY_GROUP = (
        ('whatsapp', 'whatsapp'),
        ('telegram', 'telegram'),
    )
    CATEGORY_GROUP_WHATSAPP = 'whatsapp'
    CATEGORY_GROUP_TELEGRAM = 'telegram'
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='categories_clicks', verbose_name=_('business'))
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='categories_clicks', verbose_name=_('category'))
    qr = models.ForeignKey('BusinessQR', on_delete=models.CASCADE, related_name='categories_clicks', null=True, blank=True, verbose_name=_('QR'))
    group_type = models.CharField(_('group type'), max_length=100, choices=CATEGORY_GROUP, default=CATEGORY_GROUP_WHATSAPP)

    class Meta:
        verbose_name = _('categories click')
        verbose_name_plural = _('categories clicks')

class BusinessQR(models.Model):
    name = models.CharField(_('name'), max_length=100)
    category = models.ForeignKey(BusinessQRCategories, on_delete=models.CASCADE, related_name='qrs', verbose_name=_('category'))
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='qrs', verbose_name=_('business'))
    qr_code = models.CharField(_('QR code'), max_length=100, default=generate_small_uuid, unique=True, editable=False)
    qr_img = models.ImageField(_('QR image'), upload_to='qrs/', blank=True, null=True)
    
    class Meta:
        unique_together = ('name', 'business', 'category')
        verbose_name = _('business QR')
        verbose_name_plural = _('business QRs')
    
    def __str__(self) -> str:
        return self.category.name + ' - '+  self.name
    
    def get_link(self):
        if self.qr_code:
            return settings.BACKEND_DOMAIN +  '/join/' + self.business.slug + '/?c=' + str(self.qr_code)
    
    def html_qr_img(self):
        if self.qr_img:
            return mark_safe(f'<img src="{self.qr_img.url}" width="50" height="50" />')
        return _('No Image')
    html_qr_img.short_description = _('QR Image')
    
    def save(self):
        if not self.qr_img and self.qr_code:
            link = self.get_link()
            if link:
                qr_code_img = qrcode.make(link)
                img_io = BytesIO()
                qr_code_img.save(img_io, format='PNG')
                img_io.seek(0)
                filename = f'{self.qr_code}.png'
                self.qr_img.save(filename, File(img_io), save=False)
        return super().save()
    
    def get_html_link(self):
        return mark_safe(f'<a href="{self.get_link()}">{self.get_link()}</a>')
    get_html_link.short_description = _('Link')

class WhatsappGroup(models.Model):
    name = models.CharField(_('name'), max_length=120, blank=True, null=True)
    chat_id = models.CharField(_('chat ID'), max_length=120)
    last_members_count = models.PositiveIntegerField(_('last members count'), default=0)
    last_members_check = models.DateTimeField(_('last members check'), blank=True, null=True)

    def get_link(self):
        return 'https://chat.whatsapp.com/' + self.chat_id
    
    def save(self):
        if self.chat_id.startswith('https://chat.whatsapp.com/'):
            self.chat_id = self.chat_id.replace('https://chat.whatsapp.com/', '')
        return super().save()
    
    def __str__(self) -> str:
        return self.name +' - (' +  (''.join([c.name for c in self.whatsapp_categories.all()])) + ')'

    class Meta:
        verbose_name = _('WhatsApp group')
        verbose_name_plural = _('WhatsApp groups')

class TelegramGroup(models.Model):
    name = models.CharField(_('name'), max_length=120, blank=True, null=True)
    chat_id = models.CharField(_('chat ID'), max_length=120)
    last_members_count = models.PositiveIntegerField(_('last members count'), default=0)
    last_members_check = models.DateTimeField(_('last members check'), blank=True, null=True)

    def get_link(self):
        return 'https://t.me/' + self.chat_id
    
    def save(self):
        if self.chat_id.startswith('https://t.me/'):
            self.chat_id = self.chat_id.replace('https://t.me/', '')
        return super().save()
    
    def __str__(self) -> str:
        return self.name +' - (' +  (''.join([c.name for c in self.telegram_categories.all()])) + ')'

    class Meta:
        verbose_name = _('Telegram group')
        verbose_name_plural = _('Telegram groups')

class Category(models.Model):
    icon = models.ImageField(_('icon'), upload_to='categories/', blank=True, null=True)
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, allow_unicode=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='categories', verbose_name=_('business'))
    open_whatsapp_url = models.ForeignKey(to=WhatsappGroup, on_delete=models.SET_NULL, related_name='open_whatsapp_categories', null=True, blank=True, verbose_name=_('open WhatsApp URL'))
    open_telegram_url = models.ForeignKey(to=TelegramGroup, on_delete=models.SET_NULL, related_name='open_telegram_categories', null=True, blank=True, verbose_name=_('open Telegram URL'))
    all_whatsapp_urls = models.ManyToManyField(to=WhatsappGroup, related_name='whatsapp_categories', verbose_name=_('all WhatsApp URLs'))
    all_telegram_urls = models.ManyToManyField(to=TelegramGroup, related_name='telegram_categories', verbose_name=_('all Telegram URLs'))
    
    def __str__(self) -> str:
        return self.name + ' - ' + self.business.name
    
    class Meta:
        unique_together = ('slug', 'business')
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        
    def save(self):
        return super().save()

    def image_display(self):
        if self.icon:
            return mark_safe(f'<img src="{self.icon.url}" width="50" height="50" />')
        return _('No Image')
    
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

CONTENT_STATE = (
    ('A', _('Approved')),
    ('P', _('Pending')),
    ('R', _('Rejected')),
)

class ContentSchedule(models.Model):
    id = models.UUIDField(_('ID'), primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField(_('message'), max_length=200, blank=True, null=True)
    image = models.ImageField(_('image'), upload_to='contents/', blank=True, null=True)
    send_date = models.DateTimeField(_('send date'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='contentSchedules', verbose_name=_('business'))
    approve_state = models.CharField(_('approve state'), max_length=1, choices=CONTENT_STATE, default='P')
    approve_date = models.DateTimeField(_('approve date'), blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='contentSchedules', blank=True, verbose_name=_('categories'))
    is_whatsapp_sent = models.BooleanField(_('is WhatsApp sent'), default=False)
    is_telegram_sent = models.BooleanField(_('is Telegram sent'), default=False)
    
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
        if self.updated_at and (timezone.now() - self.updated_at).seconds < 300:
            return False
        if self.send_date and self.send_date <= timezone.now():
            return True
        return False
    
    class Meta:
        ordering = ['-send_date', '-created_at']
        verbose_name = _('content schedule')
        verbose_name_plural = _('content schedules')