from django.shortcuts import render
from models.models import Business
from models.models import LeadsClicks, CategoriesClicks, BusinessQR, BizMessages
from counting.models import DaylyGroupSizeCount, WhatsappGroupSizeCount, TelegramGroupSizeCount
from django.db.models import Count
import json
# Create your views here.
def dashboard_messages(request):
    businesses = Business.objects.all()
    all_messages = BizMessages.objects.all()
    
    selected_busines = request.GET.get('business', None)
    if selected_busines:
        all_messages = all_messages.filter(business__id=selected_busines)
        
    all_messages_json = []
    # created_at,business,message,send_at,is_sent,categories
    for message in all_messages:
        all_messages_json.append({
            'id': message.id,
            'created_at': message.created_at,
            'business': message.business.name,
            'message': message.message,
            'send_at': message.send_at,
            'is_sent': message.is_sent,
            'categories': message.categories.all().values_list('name', flat=True),})
    
    all_messages_json = json.dumps(all_messages_json, default=str)
    
    return render(request, 'dashboard/messages/index.html', {
        'businesses': businesses,
        'all_messages': all_messages,
        'all_messages_json': all_messages_json,
    })

def dashboard_index(request):
    return render(request, 'dashboard/index.html', {})

def dashboard_leads_in(request):
    businesses = Business.objects.all()
    
    # queryparams filters
    busines = request.GET.get('business', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    qrs = request.GET.get('qrs', None)

    leads = LeadsClicks.objects.all()
    categories_clicks = CategoriesClicks.objects.all()
    group_size_count = DaylyGroupSizeCount.objects.prefetch_related('whatsappgroupsizecount_set', 'telegramgroupsizecount_set').all()
    qrs_list = None# BusinessQR.objects.all()
    if busines:
        leads = leads.filter(business__id=busines)
        qrs_list = BusinessQR.objects.filter(business__id=busines)
        categories_clicks = categories_clicks.filter(business__id=busines)
        group_size_count = group_size_count.filter(business__id=busines)
    if start_date:
        leads = leads.filter(created_at__gte=start_date)
        categories_clicks = categories_clicks.filter(created_at__gte=start_date)
        group_size_count = group_size_count.filter(date__gte=start_date)
    if end_date:
        leads = leads.filter(created_at__lte=end_date)
        categories_clicks = categories_clicks.filter(created_at__lte=end_date)
        group_size_count = group_size_count.filter(date__lte=end_date)
    
    # all_whatsapps_arr = []
    # all_telegrams_arr = []
    # for item in group_size_count:
    #     all_whatsapps_arr.extend(item.whatsappgroupsizecount_set.all())
    #     all_telegrams_arr.extend(item.telegramgroupsizecount_set.all())
    group_size_count_ids = group_size_count.values_list('id', flat=True)
    all_whatsapps_qs = WhatsappGroupSizeCount.objects.filter(session__id__in=group_size_count_ids)
    all_telegrams_qs = TelegramGroupSizeCount.objects.filter(session__id__in=group_size_count_ids)
    
    # keep only the last count of each group
    all_whatsapps_qs = all_whatsapps_qs.order_by('group', '-session__date').distinct('group')
    all_telegrams_qs = all_telegrams_qs.order_by('group', '-session__date').distinct('group')
    
    
    
    if qrs:
        leads = leads.filter(qr__id=qrs)
        categories_clicks = categories_clicks.filter(qr__id=qrs)
    
    
    # leads_total = leads.count()
    # categories_clicks_total = categories_clicks.count()
    # leads = leads.values('qr__name', 'qr__category__name').annotate(count=Count('id')).order_by('-count')
    # categories_clicks = categories_clicks.values('category__name',).annotate(count=Count('category__name'))
    leads_clicks_json = []
    for lead in leads:
        leads_clicks_json.append({
            'id': lead.id,
            'business': lead.business.name,
            'qr': lead.qr.name if lead.qr else '',
            'qr_category': lead.qr.category.name if lead.qr else 'אורגני',
            'type': 'כניסה לאתר',
            'count': 1,
        })
        
    categories_clicks_json = []
    for category_click in categories_clicks:
        categories_clicks_json.append({
            'id': category_click.id,
            'business': category_click.business.name,
            'category': category_click.category.name,
            'group_type': category_click.group_type,
            'qr': category_click.qr.name if category_click.qr else '',
            'qr_category': category_click.qr.category.name if category_click.qr else 'אורגני',
            'type': 'לחיצה על קטגוריה',
            'count': 1,
        })
        
    
    all_whatsapps_json = []
    for whatsapp in all_whatsapps_qs:
        all_whatsapps_json.append({
            'id': whatsapp.id,
            'business': whatsapp.session.business,
            'category' : whatsapp.group.whatsapp_categories.first().name if whatsapp.group.whatsapp_categories.first() else '',
            'group_type': 'whatsapp',
            'group': whatsapp.group.name,
            'count': whatsapp.count,
            'type': 'גודל קבוצה',
        })
        
    all_telegrams_json = []
    for telegram in all_telegrams_qs:
        all_telegrams_json.append({
            'id': telegram.id,
            'business': telegram.session.business,
            'category' : telegram.group.telegram_categories.first().name if telegram.group.telegram_categories.first() else '',
            'group_type': 'telegram',
            'group': telegram.group.name,
            'count': telegram.count,
            'type': 'גודל קבוצה',
        })
        
        
    all_whatsapps_json = json.dumps(all_whatsapps_json, default=str)
    all_telegrams_json = json.dumps(all_telegrams_json, default=str)
    leads_clicks_json = json.dumps(leads_clicks_json, default=str)
    categories_clicks_json = json.dumps(categories_clicks_json, default=str)
    return render(request, 'dashboard/leads-in/index.html', {
        # filters options qs
        'businesses': businesses,
        'qrs_list': qrs_list,
        
        
        # results
        'leads_clicks_json': leads_clicks_json,
        'categories_clicks_json': categories_clicks_json,
        'all_whatsapps_json':all_whatsapps_json,
        'all_telegrams_json':[],# all_telegrams_json
        
    })