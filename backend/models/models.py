from django.db import models

# Create your models here.
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


class Category(models.Model):
    icon = models.ImageField(upload_to='categories/', blank=True, null=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100,allow_unicode=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='categories')
    
    open_whatsapp_url = models.CharField(max_length=200, blank=True, null=True)
    open_telegram_url = models.CharField(max_length=200, blank=True, null=True)
    
    
    
    all_whatsapp_urls = models.JSONField(blank=True, null=True)
    all_telegram_urls = models.JSONField(blank=True, null=True)
    
    def __str__(self) -> str:
        return self.name + ' - ' + self.business.name
    
    class Meta:
        unique_together = ('name', 'business')


# content state options: Approved, Pending, Rejected
CONTENT_STATE = (
    ('A', 'Approved'),
    ('P', 'Pending'),
    ('R', 'Rejected'),
)

class ContentSchedule(models.Model):
    message = models.TextField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='contents/', blank=True, null=True)
    send_date = models.DateTimeField(blank=True, null=True)
    approve_telegram_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='contentSchedules')

    approve_state = models.CharField(max_length=1, choices=CONTENT_STATE, default='P')
    approve_date = models.DateTimeField(blank=True, null=True)
    reject_reason = models.TextField(max_length=200, blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='contentSchedules', blank=True)
    
    is_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-send_date', '-created_at']