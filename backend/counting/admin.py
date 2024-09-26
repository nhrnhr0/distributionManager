from django.contrib import admin
from .models import DaylyGroupSizeCount, WhatsappGroupSizeCount, TelegramGroupSizeCount, WeeklyMessagesResponsesCount
from models.models import WhatsappGroup
# Register your models here.

class WhatsappGroupSizeCountInline(admin.TabularInline):
    model = WhatsappGroupSizeCount
    extra = 1
    autocomplete_fields = ['group']

    
class TelegramGroupSizeCountInline(admin.TabularInline):
    model = TelegramGroupSizeCount
    extra = 1
    autocomplete_fields = ['group']
    


class DaylyGroupSizeCountAdmin(admin.ModelAdmin):
    list_display = ['business', 'created_at']
    inlines = [WhatsappGroupSizeCountInline, TelegramGroupSizeCountInline]
    
    pass
admin.site.register(DaylyGroupSizeCount, DaylyGroupSizeCountAdmin)

class WhatsappGroupSizeCountAdmin(admin.ModelAdmin):
    list_display = ['group', 'count', 'session']
    pass
admin.site.register(WhatsappGroupSizeCount, WhatsappGroupSizeCountAdmin)

class TelegramGroupSizeCountAdmin(admin.ModelAdmin):
    list_display = ['group', 'count', 'session']
    pass
admin.site.register(TelegramGroupSizeCount, TelegramGroupSizeCountAdmin)

class WeeklyMessagesResponsesCountAdmin(admin.ModelAdmin):
    list_display = ['business', 'date', 'count']
    pass
admin.site.register(WeeklyMessagesResponsesCount, WeeklyMessagesResponsesCountAdmin)
