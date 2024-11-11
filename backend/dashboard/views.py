from django.shortcuts import render
from api_app.views import get_group_count
from models.models import Business
from models.models import (
    LeadsClicks,
    CategoriesClicks,
    BusinessQR,
    BizMessages,
    Category,
    MessageCategory,
)
from counting.models import (
    DaylyGroupSizeCount,
    WhatsappGroupSizeCount,
    TelegramGroupSizeCount,
)
from django.db.models import Count
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
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
from counting.models import (
    DaylyGroupSizeCount,
    WhatsappGroupSizeCount,
    TelegramGroupSizeCount,
)
from django.conf import settings
from django.utils import timezone
from apscheduler.triggers.cron import CronTrigger

# from models.forms import BizMessagesForm, MessageCategoryFormSet
# Create your views here.

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(timezone="Asia/Jerusalem")
scheduler.start()


def dashboard_counting_group_size_detail(request, id):
    obj = DaylyGroupSizeCount.objects.prefetch_related(
        "whatsappgroupsizecount_set", "telegramgroupsizecount_set"
    ).get(id=id)
    return render(
        request,
        "dashboard/counting/group_size/detail.html",
        {
            "obj": obj,
        },
    )


def craete_group_size_count(request):
    data = request.POST
    business = Business.objects.get(id=data["business"])

    obj = DaylyGroupSizeCount.objects.create(business=business)
    return redirect("dashboard_counting_group_size_detail", id=obj.id)


@admin_required
def dashboard_counting_group_size(request):
    if request.method == "POST":
        return craete_group_size_count(request)
    businesses = Business.objects.all()

    counts = DaylyGroupSizeCount.objects.prefetch_related(
        "whatsappgroupsizecount_set", "telegramgroupsizecount_set"
    ).all()

    business = request.GET.get("business", None)

    if business:
        counts = counts.filter(business__id=business)

    return render(
        request,
        "dashboard/counting/group_size/index.html",
        {
            "businesses": businesses,
            "counts": counts,
        },
    )


@admin_required
def dashboard_message_new(request):
    # create new empty message with empty links and categories and return the uid
    if request.method == "POST":
        message = BizMessages.objects.create()
        return redirect("message_edit", uid=message.uid)


@admin_required
def dashboard_message_send_edit(request, uid):
    message_cat = MessageCategory.objects.get(uid=uid)

    if request.method == "POST":
        data = request.POST
        is_sent = data.get("is_sent") == "on"
        message_cat.is_sent = is_sent
        message_cat.save()

        msg = "השינויים נשמרו בהצלחה"
        messages.success(request, msg)
        return redirect("message_edit_send", uid=message_cat.uid)

    return render(
        request,
        "dashboard/messages/send/send_edit.html",
        {
            "message_cat": message_cat,
        },
    )
    pass


@admin_required
def dashboard_message_send(request):
    messages_cats = MessageCategory.objects.select_related(
        "message", "category", "message__business"
    ).all()
    # order by, first the ones that are not sent, then the ones that are sent
    # and then by the send_at date, as close as possible to now and blank dates last
    messages_cats = messages_cats.order_by("is_sent", "send_at")

    return render(
        request,
        "dashboard/messages/send/index.html",
        {
            "all_message_categories": messages_cats,
        },
    )


def monitor_telegram_notifications():
    now = timezone.now()
    messages_to_send = MessageCategory.objects.filter(
        is_sent=False,
        reminder_sent=False,
        send_at__lte=now,
        category__open_telegram_url__isnull=True,  # ודא שהקטגוריה מקושרת לקבוצת טלגרם
    )
    for msg in messages_to_send:
        send_telegram_notification(msg.uid)
        # msg.is_sent = True  # עדכון סטטוס להודעה שנשלחה
        msg.reminder_sent = True  # תיעוד שההודעה נשלחה
        msg.save()


def send_scheduled_telegram_messages():
    now = timezone.now()
    messages_to_send = MessageCategory.objects.filter(
        is_sent=False,
        send_at__lte=now,
        category__open_telegram_url__isnull=False,  # בדיקה שההודעה מיועדת לטלגרם
    )

    for msg in messages_to_send:
        logger.info(
            f"Preparing to send scheduled message UID {msg.uid} scheduled for {msg.send_at}."
        )
        try:
            chat_id = settings.TELEGRAM_CHAT_ID  # קבלת ה-chat_id של קבוצת הטלגרם
            message_text = (
                msg.get_generated_message_telegram()
            )  # יצירת תוכן ההודעה לטלגרם
            send_telegram_messege(message_text, chat_id)  # שליחה לטלגרם

            # עדכון הסטטוס להודעה שנשלחה
            msg.is_sent = True
            msg.save()
            logger.info(
                f"Scheduled message with UID {msg.uid} sent successfully to Telegram."
            )
        except AttributeError:
            logger.error(f"Chat ID not found for message UID {msg.uid}.")
        except Exception as e:
            logger.error(f"Error sending scheduled message UID {msg.uid}: {str(e)}")


def check_group_count_threshold():
    """Check if any group count exceeds 800 and send a notification if it does"""
    threshold = 800

    # חיפוש קבוצות ווטסאפ שעברו את הסף ולא נשלחה עליהן התראה
    groups_over_threshold = (
        DaylyGroupSizeCount.objects.filter(
            whatsappgroupsizecount_set__count__gt=threshold
        )
        .filter(notification_sent=False)
        .distinct()
    )

    for group in groups_over_threshold:
        groups_str = ",".join(
            list(
                group.whatsappgroupsizecount_set.filter(
                    count__gt=threshold
                ).values_list("group__name", flat=True)
            )
        )
        message = f"ספירת קבוצות ווטסאפ של '{group.business.name}' {groups_str} עברה את הסף של בקבוצה {threshold}!"
        chat_id = settings.TELEGRAM_CHAT_ID
        send_telegram_messege(message, chat_id)

        # עדכון השדה לאחר שליחת ההתרעה
        group.notification_sent = True
        group.save()

        logger.info(
            f"Notification sent for group '{group.business.name}' with count over {threshold}"
        )


def send_daily_group_count_reminder():
    """Send daily reminder at 9:00 AM for group counting"""
    message = "בצע ספירת קבוצות יומית"
    chat_id = settings.TELEGRAM_CHAT_ID
    send_telegram_messege(message, chat_id)
    logger.info("Sent daily group count reminder")


def send_weekly_whatsapp_call_reminder():
    """Send weekly reminder at 9:00 AM on Sundays for WhatsApp call counting"""
    message = "בצע ספירת שיחות וואטצאפ שבועית"
    chat_id = settings.TELEGRAM_CHAT_ID
    send_telegram_messege(message, chat_id)
    logger.info("Sent weekly WhatsApp call count reminder")


def send_telegram_notification(msg_uid):
    chat_id = settings.TELEGRAM_CHAT_ID
    backend_domain = settings.BACKEND_DOMAIN
    message = "הודעה זו צריכה להישלח\n"
    message += f"{backend_domain}/dashboard/messages-send/{msg_uid}/"

    send_telegram_messege(message, chat_id)


def send_telegram_messege(msg_txt, chat_id):
    payload = {"chat_id": chat_id, "text": msg_txt}

    response = requests.post(
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
        json=payload,
    )

    if response.status_code != 200:
        logger.error(
            f"Failed to send reminder to Telegram: {response.status_code} - {response.text}"
        )
    else:
        logger.info("Message sent succusfully.")


def setup_scheduler():
    logger.info("Setting up scheduler...")

    # Existing reminder job
    if not scheduler.get_job("unsent_messages_reminder"):
        scheduler.add_job(
            monitor_telegram_notifications,
            "interval",
            minutes=1,
            id="unsent_messages_reminder",
        )
        logger.info("Scheduled 'unsent_messages_reminder' job.")
    else:
        logger.info("'unsent_messages_reminder' job already exists.")

    # Daily group count reminder at 9:00 AM
    if not scheduler.get_job("daily_group_count_reminder"):
        scheduler.add_job(
            send_daily_group_count_reminder,
            CronTrigger(hour=9, minute=0, day_of_week="mon-fri,sun"),
            id="daily_group_count_reminder",
        )
        logger.info("Scheduled 'daily_group_count_reminder' job.")
    else:
        logger.info("'daily_group_count_reminder' job already exists.")

    # Weekly WhatsApp call count reminder at 9:00 AM on Sundays
    if not scheduler.get_job("weekly_whatsapp_call_reminder"):
        scheduler.add_job(
            send_weekly_whatsapp_call_reminder,
            CronTrigger(day_of_week="sun", hour=9, minute=0),
            id="weekly_whatsapp_call_reminder",
        )
        logger.info("Scheduled 'weekly_whatsapp_call_reminder' job.")
    else:
        logger.info("'weekly_whatsapp_call_reminder' job already exists.")

    # הוספת משימה מתוזמנת לבדיקת מכסה ספירת קבוצות יומית
    if not scheduler.get_job("check_group_count_threshold"):
        scheduler.add_job(
            check_group_count_threshold,
            "interval",
            hours=4,
            id="check_group_count_threshold",
        )
        logger.info("Scheduled 'check_group_count_threshold' job.")
    else:
        logger.info("'check_group_count_threshold' job already exists.")

    if not scheduler.get_job("send_scheduled_telegram_messages"):
        scheduler.add_job(
            send_scheduled_telegram_messages,
            "interval",
            minutes=1,  # בדיקה כל דקה, ניתן לשנות לפי הצורך
            id="send_scheduled_telegram_messages",
        )
    logger.info("Scheduled 'send_scheduled_telegram_messages' job.")

    # Log all scheduled jobs
    for job in scheduler.get_jobs():
        logger.info(f"Scheduled job: {job}")


def dashboard_message_edit(request, uid):
    message = BizMessages.objects.get(uid=uid)
    businesses = Business.objects.all()
    categories = Category.objects.all()

    if request.method == "POST":
        data = json.loads(request.body)
        logger.info(f"Received POST request for UID {uid} with data: {data}")

        # Update the main message fields first
        message.business_id = data["business"]
        message.messageTxt = data["messageTxt"]
        message.save()

        # Process links
        for link in data["links"]:
            if link.get("id") and link["isDeleted"]:
                message.links.get(id=link["id"]).delete()
            elif link.get("id") and not link["isDeleted"]:
                l = {"description": link["description"], "url": link["url"]}
                message.links.filter(id=link["id"]).update(**l)
            elif not link["isDeleted"]:
                l = {"description": link["description"], "url": link["url"]}
                message.links.create(**l)

        # Process categories and scheduling
        tz = pytz.timezone("Asia/Jerusalem")
        for category in data["categories"]:
            aware_dt = None
            if category.get("sendAt") and not category["isDeleted"]:
                try:
                    send_at = datetime.strptime(
                        category["sendAt"].replace("T", " "), "%Y-%m-%d %H:%M"
                    )
                    aware_dt = tz.localize(send_at)
                    logger.info(f"Parsed and localized sendAt as {aware_dt}")
                except ValueError as e:
                    logger.error(
                        f"Failed to parse sendAt for category ID {category.get('id')}: {e}"
                    )
                    continue

                c = {
                    "category_id": category["category"],
                    "send_at": aware_dt,
                    "is_sent": category["isSent"],
                }
                if category.get("id"):
                    message.categories.filter(id=category["id"]).update(**c)
                else:
                    message.categories.create(**c)

                # תזמון התראה עתידית אם לא סומנה כ"נשלח"
                if not category["isSent"] and aware_dt and message.messageTxt:
                    logger.info(f"Message scheduled at {aware_dt} for UID: {uid}")
            elif not category["isDeleted"]:
                c = {
                    "category_id": category["category"],
                    "send_at": None,
                    "is_sent": category["isSent"],
                }
                message.categories.create(**c)
                logger.info(
                    "Category created without scheduling due to missing send_at."
                )

    if request.method == "DELETE":
        message.delete()
        return redirect("dashboard_messages")

    return render(
        request,
        "dashboard/messages/edit.html",
        {
            "message": message,
            "businesses": businesses,
            "categories": categories,
        },
    )


@admin_required
def dashboard_messages(request):
    businesses = Business.objects.all()
    all_messages = (
        BizMessages.objects.select_related("business")
        .prefetch_related("categories", "links", "categories__category")
        .all()
    )

    selected_busines = request.GET.get("business", None)
    if selected_busines:
        all_messages = all_messages.filter(business__id=selected_busines)

    return render(
        request,
        "dashboard/messages/index.html",
        {
            "businesses": businesses,
            "all_messages": all_messages,
        },
    )


@admin_required
def dashboard_index(request):
    return render(request, "dashboard/index.html", {})


from counting.models import CallsResponsesCount, MessagesResponsesCount
from models.models import MessageLinkClick


@admin_required
def dashboard_leads_out(request):
    businesses = Business.objects.all()

    selected_busines = request.GET.get("business", None)
    start_date = request.GET.get("start_date", None)
    end_date = request.GET.get("end_date", None)

    calls = CallsResponsesCount.objects.all()
    messages = MessagesResponsesCount.objects.all()
    links_clicks = MessageLinkClick.objects.all()
    group_size_count = DaylyGroupSizeCount.objects.prefetch_related(
        "whatsappgroupsizecount_set", "telegramgroupsizecount_set"
    ).all()

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
            "amount": calls.last().count - calls.first().count,
            "growth": (calls.last().count - calls.first().count)
            / (calls.last().date - calls.first().date).days,
            "counts": calls.count(),
        }
    else:
        calls_info = {
            "amount": 0,
            "growth": 0,
            "counts": 0,
        }

    if messages.count() > 1:
        chats_info = {
            "amount": messages.last().count - messages.first().count,
            "growth": (messages.last().count - messages.first().count)
            / (messages.last().date - messages.first().date).days,
            "counts": messages.count(),
        }
    else:
        chats_info = {
            "amount": 0,
            "growth": 0,
            "counts": 0,
        }

    links_clicks_json = []
    for link in links_clicks:
        links_clicks_json.append(
            {
                "id": link.id,
                "business": link.msg.business.name,
                "category": link.category.name,
                "group_type": link.group_type,
                "link": link.link.description,
                "date": link.created_at,
                "count": 1,
            }
        )

    links_clicks_json = json.dumps(links_clicks_json, default=str)

    group_size_count_ids = group_size_count.values_list("id", flat=True)
    all_whatsapps_qs_full = (
        WhatsappGroupSizeCount.objects.prefetch_related("group__whatsapp_categories")
        .select_related("session")
        .filter(session__id__in=group_size_count_ids)
    )
    all_telegrams_qs_full = (
        TelegramGroupSizeCount.objects.prefetch_related("group__telegram_categories")
        .select_related("session")
        .filter(session__id__in=group_size_count_ids)
    )
    whatsapp_growth = get_group_count(all_whatsapps_qs_full, group_type="whatsapp")
    telegram_growth = get_group_count(all_telegrams_qs_full, group_type="telegram")
    for growth in whatsapp_growth:
        growth[1] = "W " + growth[1]
    for growth in telegram_growth:
        growth[1] = "T " + growth[1]
    all_growth = whatsapp_growth + telegram_growth
    all_growth = json.dumps(all_growth, default=str)
    ctx = {
        "businesses": businesses,
        "calls_info": calls_info,
        "chats_info": chats_info,
        "links_clicks_json": links_clicks_json,
        "all_growth": all_growth,
    }
    return render(request, "dashboard/leads-out/index.html", ctx)


def messages_qs_to_json(messages):
    msgs = []
    for message in messages:
        msgs.append(
            {
                "id": message.id,
                "category": message.category.name,
                "business": message.category.business.name,
                "send_at": message.send_at,
                "is_sent": message.is_sent,
                "message": message.message.messageTxt,
                "message_id": message.message.id,
                "message_uid": message.message.uid,
            }
        )
    msgs = json.dumps(msgs, default=str)
    return msgs


@admin_required
def dashboard_messages_calendar_set_date(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = MessageCategory.objects.get(id=data["id"])
        message.send_at = data["new_date"]
        message.save()
        return JsonResponse({"status": "ok"})
    pass


@admin_required
def dashboard_messages_calendar(request):
    businesses = Business.objects.all()
    messages_to_send = MessageCategory.objects.select_related(
        "category", "message"
    ).filter(category__isnull=False)
    selected_busines = request.GET.get("business", None)

    if selected_busines:
        messages_to_send = messages_to_send.filter(
            message__business__id=selected_busines
        )

    msgs = messages_qs_to_json(messages_to_send)
    return render(
        request,
        "dashboard/calender/index.html",
        {
            "businesses": businesses,
            "msgs": msgs,
        },
    )


@admin_required
def dashboard_leads_in(request):
    businesses = Business.objects.all()

    # queryparams filters
    busines = request.GET.get("business", None)
    start_date = request.GET.get("start_date", None)
    end_date = request.GET.get("end_date", None)
    qrs = request.GET.getlist("qrs", [])

    leads = LeadsClicks.objects.select_related("business", "qr", "qr__category").all()
    categories_clicks = CategoriesClicks.objects.select_related(
        "business", "qr", "qr__category", "category"
    ).all()
    group_size_count = DaylyGroupSizeCount.objects.prefetch_related(
        "whatsappgroupsizecount_set", "telegramgroupsizecount_set"
    ).all()
    qrs_list = BusinessQR.objects.all()
    sent_messages = (
        MessageCategory.objects.select_related("category")
        .filter(is_sent=True)
        .filter(category__isnull=False)
    )
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
    group_size_count_ids = group_size_count.values_list("id", flat=True)
    all_whatsapps_qs_full = (
        WhatsappGroupSizeCount.objects.prefetch_related("group__whatsapp_categories")
        .select_related("session")
        .filter(session__id__in=group_size_count_ids)
    )
    all_telegrams_qs_full = (
        TelegramGroupSizeCount.objects.prefetch_related("group__telegram_categories")
        .select_related("session")
        .filter(session__id__in=group_size_count_ids)
    )

    # keep only the last count of each group
    # all_whatsapps_qs = all_whatsapps_qs_full.order_by('group', '-session__date').distinct('group')
    # all_telegrams_qs = all_telegrams_qs_full.order_by('group', '-session__date').distinct('group')

    # remove empty strings from qrs
    qrs = list(filter(None, qrs))
    if qrs and len(qrs) > 0:
        organic = True if "0" in qrs else False

        # if organic get all loads with qr__id = None and qr__id__in=qrs
        if organic:
            leads = leads.filter(Q(qr__id__in=qrs) | Q(qr__id=None))
            categories_clicks = categories_clicks.filter(
                Q(qr__id__in=qrs) | Q(qr__id=None)
            )
        else:
            leads = leads.filter(qr__id__in=qrs)
            categories_clicks = categories_clicks.filter(qr__id__in=qrs)

    leads_clicks_json = []
    for lead in leads:
        leads_clicks_json.append(
            {
                "id": lead.id,
                "business": lead.business.name,
                "qr": lead.qr.name if lead.qr else "",
                "qr_category": lead.qr.category.name if lead.qr else "אורגני",
                "type": "כניסה לאתר",
                "count": 1,
            }
        )

    categories_clicks_json = []
    for category_click in categories_clicks:
        categories_clicks_json.append(
            {
                "id": category_click.id,
                "business": category_click.business.name,
                "category": category_click.category.name,
                "group_type": category_click.group_type,
                "qr": category_click.qr.name if category_click.qr else "",
                "qr_category": (
                    category_click.qr.category.name if category_click.qr else "אורגני"
                ),
                "type": "לחיצה על קטגוריה",
                "count": 1,
            }
        )

    whatsapp_growth = get_group_count(all_whatsapps_qs_full, group_type="whatsapp")
    telegram_growth = get_group_count(all_telegrams_qs_full, group_type="telegram")

    send_messages_count_by_group = {}  # {T category name / W category name: count}
    for message in sent_messages:
        key = message.category.name
        if key in send_messages_count_by_group:
            send_messages_count_by_group[key] += 1
        else:
            send_messages_count_by_group[key] = 1

    send_messages_count_by_group = json.dumps(send_messages_count_by_group, default=str)

    for growth in whatsapp_growth:
        growth[1] = "W " + growth[1]
    for growth in telegram_growth:
        growth[1] = "T " + growth[1]
    all_growth = whatsapp_growth + telegram_growth
    all_growth = json.dumps(all_growth, default=str)
    leads_clicks_json = json.dumps(leads_clicks_json, default=str)
    categories_clicks_json = json.dumps(categories_clicks_json, default=str)
    return render(
        request,
        "dashboard/leads-in/index.html",
        {
            # filters options qs
            "businesses": businesses,
            "qrs_list": qrs_list,
            # results
            "leads_clicks_json": leads_clicks_json,
            "categories_clicks_json": categories_clicks_json,
            "all_growth": all_growth,
            "send_messages_count_by_group": send_messages_count_by_group,
        },
    )


setup_scheduler()
