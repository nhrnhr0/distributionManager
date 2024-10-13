from django.shortcuts import render
from api_app.views import get_group_count
from models.models import Business
from models.models import LeadsClicks, CategoriesClicks, BusinessQR, BizMessages, Category,MessageCategory
from counting.models import DaylyGroupSizeCount, WhatsappGroupSizeCount, TelegramGroupSizeCount
from django.db.models import Count
import json
import pytz
from datetime import datetime
from django.contrib import messages
from core.decoretors import admin_required
from django.db.models import Q

from django.shortcuts import redirect
# from models.forms import BizMessagesForm, MessageCategoryFormSet
# Create your views here.

@admin_required
def dashboard_message_new(request):
    # create new empty message with empty links and categories and return the uid
    if request.method == 'POST':
        message = BizMessages.objects.create()
        return redirect('message_edit', uid=message.uid)
    

@admin_required
def dashboard_message_send_edit(request, uid):
    message_cat = MessageCategory.objects.get(uid=uid)
    
    if request.method == 'POST':
        data = request.POST        
        is_sent = data.get('is_sent') == 'on'
        message_cat.is_sent = is_sent
        message_cat.save()
        
        msg = "השינויים נשמרו בהצלחה"
        messages.success(request, msg)
        return redirect('message_edit_send', uid=message_cat.uid)
        
    return render(request, 'dashboard/messages/send/send_edit.html', {
        'message_cat': message_cat,
    })
    pass

@admin_required
def dashboard_message_send(request):
    messages_cats = MessageCategory.objects.select_related('message', 'category', 'message__business').all()
    # order by, first the ones that are not sent, then the ones that are sent
    # and then by the send_at date, as close as possible to now and blank dates last
    messages_cats = messages_cats.order_by('is_sent', 'send_at')
    
    return render(request, 'dashboard/messages/send/index.html', {
        'all_message_categories': messages_cats,
    })

@admin_required
def dashboard_message_edit(request, uid):
    message = BizMessages.objects.get(uid=uid)
    businesses = Business.objects.all()
    categories = Category.objects.all()
    
    if request.method == 'POST':
        data = request.body
        data = json.loads(data) 
        # first delete all links with id and isDeleted = True
        for link in data['links']:
            if link.get('id') and link['isDeleted']:
                message.links.get(id=link['id']).delete()
        # then update or create the rest
        for link in data['links']:
            if link.get('id') and not link['isDeleted']:
                l = {'description': link['description'], 'url': link['url']}
                message.links.filter(id=link['id']).update(**l)
            elif not link['isDeleted']:
                l = {'description': link['description'], 'url': link['url']}
                message.links.create(**l)

        # first delete all categories with id and isDeleted = True
        for category in data['categories']:
            if category.get('id') and category['isDeleted']:
                message.categories.get(id=category['id']).delete()
        # then update or create the rest
        tz = pytz.timezone('Asia/Jerusalem')

        for category in data['categories']:
            if category.get('id') and not category['isDeleted']:
                if category['sendAt']:
                    category['sendAt'] =  datetime.strptime(category['sendAt'].replace('T', ' '), '%Y-%m-%d %H:%M')
                    aware_dt = tz.localize(category['sendAt'])
                    category['sendAt'] = aware_dt
                c = {'category_id': category['category'], 'send_at': category['sendAt'] if category['sendAt'] else None, 'is_sent': category['isSent']}
                message.categories.filter(id=category['id']).update(**c)
            elif not category['isDeleted']:
                if category['sendAt']:
                    category['sendAt'] =  datetime.strptime(category['sendAt'].replace('T', ' '), '%Y-%m-%d %H:%M')
                    aware_dt = tz.localize(category['sendAt'])
                    category['sendAt'] = aware_dt
                    
                c = {'category_id': category['category'], 'send_at': category['sendAt'] if category['sendAt'] else None, 'is_sent': category['isSent']}
                message.categories.create(**c)

        message.business_id = data['business']
        message.messageTxt = data['messageTxt']
        message.save()
    
    if request.method == 'DELETE':
        message.delete()
        return redirect('dashboard_messages')
    return render(request, 'dashboard/messages/edit.html', {
        'message': message,
        'businesses': businesses,
        'categories': categories,
    })


@admin_required
def dashboard_messages(request):
    businesses = Business.objects.all()
    all_messages = BizMessages.objects.select_related('business').prefetch_related('categories', 'links', 'categories__category').all()
    
    selected_busines = request.GET.get('business', None)
    if selected_busines:
        all_messages = all_messages.filter(business__id=selected_busines)
        
    return render(request, 'dashboard/messages/index.html', {
        'businesses': businesses,
        'all_messages': all_messages,
    })



@admin_required
def dashboard_index(request):
    return render(request, 'dashboard/index.html', {})






from counting.models import CallsResponsesCount, MessagesResponsesCount
from models.models import MessageLinkClick
@admin_required
def dashboard_leads_out(request):
    businesses = Business.objects.all()

    selected_busines = request.GET.get('business', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    
    calls = CallsResponsesCount.objects.all()
    messages = MessagesResponsesCount.objects.all()
    links_clicks = MessageLinkClick.objects.all()
    group_size_count = DaylyGroupSizeCount.objects.prefetch_related('whatsappgroupsizecount_set', 'telegramgroupsizecount_set').all()
    
    if selected_busines:
        calls = calls.filter(business__id=selected_busines)
        messages = messages.filter(business__id=selected_busines)
        links_clicks = links_clicks.filter(msg__business__id=selected_busines)
        group_size_count = group_size_count.filter(business__id=selected_busines)
        
    if start_date:
        calls = calls.filter(date__gte=start_date)
        messages = messages.filter(date__gte=start_date)
        links_clicks = links_clicks.filter(created_at__gte=start_date)
        group_size_count = group_size_count.filter(date__gte=start_date)
    
    if end_date:
        calls = calls.filter(date__lte=end_date)
        messages = messages.filter(date__lte=end_date)
        links_clicks = links_clicks.filter(created_at__lte=end_date)
        group_size_count = group_size_count.filter(date__lte=end_date)

    if calls.count() > 0:
        calls_info = {
            'amount': calls.last().count - calls.first().count,
            'growth': (calls.last().count - calls.first().count) / (calls.last().date - calls.first().date).days,
            'counts': calls.count(),
        }
    else:
        calls_info = {
            'amount': 0,
            'growth': 0,
            'counts': 0,
        }
        
    if messages.count() > 0:
        chats_info = {
            'amount': messages.last().count - messages.first().count,
            'growth': (messages.last().count - messages.first().count) / (messages.last().date - messages.first().date).days,
            'counts': messages.count(),
        }
    else:
        chats_info = {
            'amount': 0,
            'growth': 0,
            'counts': 0,
        }
    
    
    links_clicks_json = []
    for link in links_clicks:
        links_clicks_json.append({
            'id': link.id,
            'business': link.msg.business.name,
            'category': link.category.name,
            'group_type': link.group_type,
            'link': link.link.description,
            'date': link.created_at,
            'count': 1,
        })
    
    links_clicks_json = json.dumps(links_clicks_json, default=str)
    
    group_size_count_ids = group_size_count.values_list('id', flat=True)
    all_whatsapps_qs_full = WhatsappGroupSizeCount.objects.prefetch_related('group__whatsapp_categories').select_related('session').filter(session__id__in=group_size_count_ids)
    all_telegrams_qs_full = TelegramGroupSizeCount.objects.prefetch_related('group__telegram_categories').select_related('session').filter(session__id__in=group_size_count_ids)
    whatsapp_growth = get_group_count(all_whatsapps_qs_full, group_type='whatsapp')
    telegram_growth = get_group_count(all_telegrams_qs_full, group_type='telegram')
    for growth in whatsapp_growth:
        growth[1] = 'W ' + growth[1]
    for growth in telegram_growth:
        growth[1] = 'T ' + growth[1]
    all_growth = whatsapp_growth + telegram_growth
    all_growth= json.dumps(all_growth, default=str)
    ctx = {
        'businesses': businesses,
        'calls_info': calls_info,
        'chats_info': chats_info,
        'links_clicks_json': links_clicks_json,
        'all_growth': all_growth
    }
    return render(request, 'dashboard/leads-out/index.html', ctx)


@admin_required
def dashboard_leads_in(request):
    businesses = Business.objects.all()
    
    # queryparams filters
    busines = request.GET.get('business', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    qrs = request.GET.getlist('qrs', [])

    leads = LeadsClicks.objects.select_related('business', 'qr', 'qr__category').all()
    categories_clicks = CategoriesClicks.objects.select_related('business', 'qr', 'qr__category', 'category').all()
    group_size_count = DaylyGroupSizeCount.objects.prefetch_related('whatsappgroupsizecount_set', 'telegramgroupsizecount_set').all()
    qrs_list = BusinessQR.objects.all()
    if busines:
        leads = leads.filter(business__id=busines)
        qrs_list = qrs_list.filter(business__id=busines)
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
    all_whatsapps_qs_full = WhatsappGroupSizeCount.objects.prefetch_related('group__whatsapp_categories').select_related('session').filter(session__id__in=group_size_count_ids)
    all_telegrams_qs_full = TelegramGroupSizeCount.objects.prefetch_related('group__telegram_categories').select_related('session').filter(session__id__in=group_size_count_ids)
    
    # keep only the last count of each group
    # all_whatsapps_qs = all_whatsapps_qs_full.order_by('group', '-session__date').distinct('group')
    # all_telegrams_qs = all_telegrams_qs_full.order_by('group', '-session__date').distinct('group')
    
    
    # remove empty strings from qrs
    qrs = list(filter(None, qrs))
    if qrs and len(qrs) > 0:
        organic = True if '0' in qrs else False
        
        # if organic get all loads with qr__id = None and qr__id__in=qrs
        if organic:
            leads = leads.filter(Q(qr__id__in=qrs) | Q(qr__id=None))
            categories_clicks = categories_clicks.filter(Q(qr__id__in=qrs) | Q(qr__id=None))
        else:
            leads = leads.filter(qr__id__in=qrs)
            categories_clicks = categories_clicks.filter(qr__id__in=qrs)


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
    
    whatsapp_growth = get_group_count(all_whatsapps_qs_full, group_type='whatsapp')
    telegram_growth = get_group_count(all_telegrams_qs_full, group_type='telegram')
    for growth in whatsapp_growth:
        growth[1] = 'W ' + growth[1]
    for growth in telegram_growth:
        growth[1] = 'T ' + growth[1]
    all_growth = whatsapp_growth + telegram_growth
    all_growth= json.dumps(all_growth, default=str)
    leads_clicks_json = json.dumps(leads_clicks_json, default=str)
    categories_clicks_json = json.dumps(categories_clicks_json, default=str)
    return render(request, 'dashboard/leads-in/index.html', {
        # filters options qs
        'businesses': businesses,
        'qrs_list': qrs_list,
        
        # results
        'leads_clicks_json': leads_clicks_json,
        'categories_clicks_json': categories_clicks_json,
        'all_growth': all_growth
        
    })