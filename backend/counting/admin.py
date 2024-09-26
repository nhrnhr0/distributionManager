from django.contrib import admin
from .models import DaylyGroupSizeCount, WhatsappGroupSizeCount, TelegramGroupSizeCount, MessagesResponsesCount, CallsResponsesCount
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
    list_display = ['business', 'date']
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

class MessagesResponsesCountAdmin(admin.ModelAdmin):
    list_display = ['business', 'date', 'count']
    pass
admin.site.register(MessagesResponsesCount, MessagesResponsesCountAdmin)

class CallsResponsesCountAdmin(admin.ModelAdmin):
    list_display = ['business', 'date', 'count']
    pass
admin.site.register(CallsResponsesCount, CallsResponsesCountAdmin)
