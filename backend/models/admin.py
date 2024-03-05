from django.contrib import admin
from .models import SysUser, Business, Category, ContentSchedule,TelegramGroup, WhatsappGroup
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
# Register your models here.
class SysUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']
    pass
admin.site.register(SysUser, SysUserAdmin)


class BusinessAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'all_users']
    prepopulated_fields = {'slug': ('name',)}

    def all_users(self, obj):
        return ', '.join([user.name for user in obj.users.all()])

    pass
admin.site.register(Business, BusinessAdmin)

class WhatsappInline(admin.TabularInline):
    model=Category.all_whatsapp_urls.through
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ['id', 'image_display', 'name', 'slug', 'business','whatsapp_groups_count', 'telegram_groups_count']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['image_display', 'whatsapp_groups_count','telegram_groups_count']
    inlines= [WhatsappInline]
    search_fields = ['name', 'business__name']
    list_filter = ['business',]
    exclude = ['all_whatsapp_urls', 'all_telegram_urls',]
    
    def image_display(self, obj):
        if obj.icon:
            return mark_safe(f'<img src="{obj.icon.url}" width="50" height="50" />')
        return 'No Image'
    image_display.short_description = 'Icon'
    
    def whatsapp_groups_count(self, obj: Category):
        return obj.all_whatsapp_urls.count()
        pass
    def telegram_groups_count(self, obj: Category):
        return obj.all_telegram_urls.count()

        pass

    pass
admin.site.register(Category, CategoryAdmin)
class ContentScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'image', 'created_at', 'updated_at', 'business', 'approve_state', 'approve_date']
    filter_horizontal = ['categories']
    readonly_fields = ['created_at', 'updated_at', 'approve_date', 'approve_state',]
    list_filter = ['business', 'categories', 'approve_state', 'send_date']
    pass
admin.site.register(ContentSchedule, ContentScheduleAdmin)


class WhatsappGroupAdmin(admin.ModelAdmin):
    list_display= ('id','name', 'chat_id', 'get_link')
    readonly_fields = ('get_link',)
    
    pass
admin.site.register(WhatsappGroup, WhatsappGroupAdmin)
class TelegramGroupAdmin(admin.ModelAdmin):

    pass
admin.site.register(TelegramGroup, TelegramGroupAdmin)