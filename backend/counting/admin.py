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
    actions = ['download_csv',]
    
    def download_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        import io
        f = io.StringIO()
        writer = csv.writer(f)
        writer.writerow(['business', 'date', 'category','group', 'group type'])
        queryset = queryset.prefetch_related('whatsappgroupsizecount_set', 'telegramgroupsizecount_set')
        for s in queryset:
            for w in s.whatsappgroupsizecount_set.all():
                category = w.group.whatsapp_categories.first()
                category_name = category.name if category else None
                for c in range(w.count):
                    writer.writerow([s.business, s.date, category_name, w.group, 'whatsapp'])
            for t in s.telegramgroupsizecount_set.all():
                category = t.group.telegram_categories.first()
                category_name = category.name if category else None
                for c in range(t.count):
                    writer.writerow([s.business, s.date, category_name, t.group, 'telegram'])
        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=dayly_group_size_count.csv'
        return response
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
