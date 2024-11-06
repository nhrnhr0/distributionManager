from django.shortcuts import render
from api_app.views import get_group_count
from models.models import Business
from models.models import LeadsClicks, CategoriesClicks, BusinessQR, BizMessages, Category,MessageCategory
from counting.models import DaylyGroupSizeCount, WhatsappGroupSizeCount, TelegramGroupSizeCount
from django.db.models import Count
from apscheduler.schedulers.background import BackgroundScheduler
from django.http import HttpResponse, HttpResponseBadRequest
import json
import pytz
import logging
import requests
from datetime import datetime
from django.contrib import messages
from core.decoretors import admin_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from counting.models import DaylyGroupSizeCount, WhatsappGroupSizeCount, TelegramGroupSizeCount
from django.conf import settings

# from models.forms import BizMessagesForm, MessageCategoryFormSet
# Create your views here.

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(timezone='Asia/Jerusalem')
scheduler.start()

def dashboard_counting_group_size_detail(request, id):
    obj = DaylyGroupSizeCount.objects.prefetch_related('whatsappgroupsizecount_set', 'telegramgroupsizecount_set').get(id=id)
    return render(request, 'dashboard/counting/group_size/detail.html', {
        'obj': obj,
    })

def craete_group_size_count(request):
    data = request.POST
    business = Business.objects.get(id=data['business'])

    obj = DaylyGroupSizeCount.objects.create(business=business)
    return redirect('dashboard_counting_group_size_detail', id=obj.id)

@admin_required
def dashboard_counting_group_size(request):
    if request.method == 'POST':
        return craete_group_size_count(request)
    businesses = Business.objects.all()
    
    counts = DaylyGroupSizeCount.objects.prefetch_related('whatsappgroupsizecount_set', 'telegramgroupsizecount_set').all()

    business = request.GET.get('business', None)
    
    if business:
        counts = counts.filter(business__id=business)
    
    return render(request, 'dashboard/counting/group_size/index.html', {
        'businesses': businesses,
        'counts': counts,
    })

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


# def send_telegram_message(uid):
#     url = f"http://192.168.50.73:8000/dashboard/messages/edit/{uid}/"
    
#     text = f"הגיע הזמן לפרסם הודעה זו: {url}"
    
#     payload = {
#         'chat_id': settings.TELEGRAM_CHAT_ID,
#         'text': text
#     }
    
#     response = requests.post(f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage", json=payload)
    
#     if response.status_code != 200:
#         logger.error(f"Failed to send message to Telegram: {response.text}")
#     return response.status_code == 200

# def schedule_telegram_message(uid, send_at):
#     try:
#         job = scheduler.add_job(
#             send_telegram_message,
#             'date',
#             run_date=send_at,
#             args=[uid]
#         )
#         logger.info (f"scheduled job: {job.id}, run at {send_at} for UID: {uid}")
#     except Exception as e:
#             logger.error(f"failed to schedule job for UID {uid}: {e}")


def send_telegram_message():
    try:
        # Fetch only unsent messages
        unsent_messages = MessageCategory.objects.filter(is_sent=False)
        
        if unsent_messages.exists():
            # Construct message text with each unsent message link
            text = "הודעות שלא נשלחו:\n"
            for message in unsent_messages:
                url = f"http://192.168.50.73:8000/dashboard/messages-send/{message.uid}/"
                text += f"{message.uid}: {url}\n"

            payload = {
                'chat_id': settings.TELEGRAM_CHAT_ID,
                'text': text
            }
            
            response = requests.post(f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage", json=payload)
            
            if response.status_code != 200:
                logger.error(f"Failed to send reminder to Telegram: {response.status_code} - {response.text}")
        else:
            logger.info("No unsent messages to send reminder for.")
    except requests.exceptions.RequestException as e:
        # Log network-related errors (e.g., connection errors)
        logger.error(f"Network error occurred when sending reminder to Telegram: {e}")
    except Exception as e:
        # Catch any other unexpected exceptions
        logger.error(f"An unexpected error occurred: {e}")
        
        
def schedule_telegram_message(uid, send_at):
    try:
        job_id = f"send_message_{uid}_{send_at.timestamp()}"
        
        # Schedule the job to run at the specified date and time
        job = scheduler.add_job(
            send_telegram_message,   
            trigger='date',
            run_date=send_at,
            id=job_id
        )
        logger.info(f"Scheduled job: {job.id}, run at {send_at} for UID: {uid}")
    except Exception as e:
        logger.error(f"Failed to schedule job for UID {uid}: {e}")


# Ensure that this job runs every minute to send reminders for unsent messages
def setup_scheduler():
    if not scheduler.get_job("unsent_messages_reminder"):
        scheduler.add_job(
            send_telegram_message,
            'interval',
            minutes=20,
            id="unsent_messages_reminder"
        )


def dashboard_message_edit(request, uid):
    message = BizMessages.objects.get(uid=uid)
    businesses = Business.objects.all()
    categories = Category.objects.all()
    
    if request.method == 'POST':
        data = json.loads(request.body)
        logger.info(f"Received POST request for UID {uid} with data: {data}")

        # Update the main message fields first
        message.business_id = data['business']
        message.messageTxt = data['messageTxt']
        message.save()

        # Process links
        for link in data['links']:
            if link.get('id') and link['isDeleted']:
                message.links.get(id=link['id']).delete()
            elif link.get('id') and not link['isDeleted']:
                l = {'description': link['description'], 'url': link['url']}
                message.links.filter(id=link['id']).update(**l)
            elif not link['isDeleted']:
                l = {'description': link['description'], 'url': link['url']}
                message.links.create(**l)

        # Process categories and scheduling
        tz = pytz.timezone('Asia/Jerusalem')
        for category in data['categories']:
            aware_dt = None
            if category.get('sendAt') and not category['isDeleted']:
                try:
                    send_at = datetime.strptime(category['sendAt'].replace('T', ' '), '%Y-%m-%d %H:%M')
                    aware_dt = tz.localize(send_at)
                    logger.info(f"Parsed and localized sendAt as {aware_dt}")
                except ValueError as e:
                    logger.error(f"Failed to parse sendAt for category ID {category.get('id')}: {e}")
                    continue

                c = {
                    'category_id': category['category'],
                    'send_at': aware_dt,
                    'is_sent': category['isSent']
                }
                if category.get('id'):
                    message.categories.filter(id=category['id']).update(**c)
                else:
                    message.categories.create(**c)

                if aware_dt and message.messageTxt:
                    schedule_telegram_message(message.uid, aware_dt)
                    logger.info(f"Message scheduled at {aware_dt} for UID: {uid}")
                elif aware_dt:
                    logger.warning("Message text is empty; nothing scheduled.")
                else:
                    logger.warning("No valid datetime; nothing scheduled.")
            elif not category['isDeleted']:
                c = {
                    'category_id': category['category'],
                    'send_at': None,
                    'is_sent': category['isSent']
                }
                message.categories.create(**c)
                logger.info("Category created without scheduling due to missing send_at.")
    
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

    if calls.count() > 1:
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
        
    if messages.count() > 1:
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

def messages_qs_to_json(messages):
    msgs = []
    for message in messages:
        msgs.append({
            'id': message.id,
            
            'category': message.category.name,
            'business': message.category.business.name,
            'send_at': message.send_at,
            'is_sent': message.is_sent,
            'message': message.message.messageTxt,
            'message_id': message.message.id,
            'message_uid': message.message.uid,
        })
    msgs = json.dumps(msgs, default=str)
    return msgs


@admin_required
def dashboard_messages_calendar_set_date(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = MessageCategory.objects.get(id=data['id'])
        message.send_at = data['new_date']
        message.save()
        return JsonResponse({'status': 'ok'})
    pass

@admin_required
def dashboard_messages_calendar(request):
    businesses = Business.objects.all()
    messages_to_send = MessageCategory.objects.select_related('category','message').filter(category__isnull=False)
    selected_busines = request.GET.get('business', None)
    
    if selected_busines:
        messages_to_send = messages_to_send.filter(message__business__id=selected_busines)
    
    msgs = messages_qs_to_json(messages_to_send)
    return render(request, 'dashboard/calender/index.html', {
        'businesses': businesses,
        'msgs': msgs,
        
    })



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
    sent_messages = MessageCategory.objects.select_related('category').filter(is_sent=True).filter(category__isnull=False)
    if busines:
        leads = leads.filter(business__id=busines)
        qrs_list = qrs_list.filter(business__id=busines)
        categories_clicks = categories_clicks.filter(business__id=busines)
        group_size_count = group_size_count.filter(business__id=busines)
    if start_date:
        leads = leads.filter(created_at__gte=start_date)
        categories_clicks = categories_clicks.filter(created_at__gte=start_date)
        group_size_count = group_size_count.filter(date__gte=start_date)
        sent_messages = sent_messages.filter(send_at__gte=start_date)
    if end_date:
        leads = leads.filter(created_at__lte=end_date)
        categories_clicks = categories_clicks.filter(created_at__lte=end_date)
        group_size_count = group_size_count.filter(date__lte=end_date)
        sent_messages = sent_messages.filter(send_at__lte=end_date)
    
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
    
    
    send_messages_count_by_group = {} # {T category name / W category name: count}
    for message in sent_messages:
        key = message.category.name
        if key in send_messages_count_by_group:
            send_messages_count_by_group[key] += 1
        else:
            send_messages_count_by_group[key] = 1
    
    send_messages_count_by_group = json.dumps(send_messages_count_by_group, default=str)
    
    
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
        'all_growth': all_growth,
        'send_messages_count_by_group': send_messages_count_by_group,
        
    })
