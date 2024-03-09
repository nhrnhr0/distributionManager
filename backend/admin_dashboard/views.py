from django.shortcuts import render
from models.models import ContentSchedule,Business
# is admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.shortcuts import render,redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from datetime import datetime
from datetime import timedelta
from django.http import HttpResponse
from django.utils import timezone

def apply_date_filter(queryset, date_filter, field_name):
    today = datetime.now()
    if date_filter == 'today':
        queryset = queryset.filter(**{field_name: today})
    elif date_filter == 'past_7_days':
        queryset = queryset.filter(**{field_name + '__gte': today - timedelta(days=7)})
    elif date_filter == 'this_month':
        queryset = queryset.filter(**{field_name + '__month': today.month})
    elif date_filter == 'this_year':
        queryset = queryset.filter(**{field_name + '__year': today.year})
    elif date_filter == 'isnull':
        queryset = queryset.filter(**{field_name + '__isnull': True})
    elif date_filter == 'notnull':
        queryset = queryset.filter(**{field_name + '__isnull': False})
    return queryset
@login_required
def admin_dashboard_schedule(request):
    if request.user.groups.filter(name='content editor').count() == 0:
        return error_page("למשתמש אין הרשאת עריכה לעסק")
    biz = request.user.me.business
    # filter based on query params
    messages = ContentSchedule.objects.filter(business=biz)
    if request.GET.get('approve_state'):
        approve_state = request.GET.get('approve_state')
        messages = messages.filter(approve_state=approve_state)
    if request.GET.get('send_date'):
        # send_date=today
        # send_date=past_7_days
        # send_date=this_month
        # send_date__isnull=True / False
        send_date = request.GET.get('send_date')
        messages = apply_date_filter(messages, send_date, 'send_date')
            
    return render(request, 'admin_dashboard/messages.html', {'biz_messages': messages})

@login_required
def admin_dashboard_message_detail(request, id=None):
    if request.user.groups.filter(name='content editor').count() == 0:
        return error_page("למשתמש אין הרשאת עריכה לעסק")
    message = None
    if id:
        message = ContentSchedule.objects.get(id=id)
        if message.business != request.user.me.business:
            return error_page('משאב זה אינו שייך לך')
    if request.method == 'POST':
        #image,message,send_date,categories
        id = request.POST.get('id')
        message = request.POST.get('message')
        send_date = request.POST.get('send_date','') if request.POST.get('send_date','') else None
        image = request.FILES.get('image')
        categories = request.POST.getlist('categories')
        approve_state = request.POST.get('approve_state')
        try:
            if id:
                obj = ContentSchedule.objects.get(id=id)
                obj.message = message
                obj.send_date = send_date
                if obj.image:
                    obj.image = image
            else:
                obj = ContentSchedule.objects.create(
                    message=message,
                    send_date=send_date,
                    image=image,
                    business=request.user.me.business
                )
            
            obj.categories.set(categories)
            if obj.approve_state != approve_state:
                obj.approve_state = approve_state
                if obj.approve_state == 'A':
                    obj.approve_date = timezone.now()
                print('approve_state updated', approve_state)

            obj.save()
            messages.add_message(request, messages.SUCCESS, 'הודעה נשמרה בהצלחה')
            action = request.POST.get('action')
            if action == 'save':
                return redirect('admin_dashboard_schedule')
            elif action == 'save_and_add_another':
                return redirect('message_new')
            elif action == 'save_and_continue_editing':
                return redirect('message_detail', id=obj.id)
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'Error: ' + str(e))

        pass
    return render(request, 'admin_dashboard/message_detail.html', {'message': message})


@login_required
def admin_dashboard_send_messages(request):
    if request.user.groups.filter(name='sender').count() == 0:
        return error_page("למשתמש אין הרשאת שליחה לעסק")
    biz = request.user.me.business
    biz_messages =  ContentSchedule.objects.filter(business=biz,approve_state='A')
    return render(request, "admin_dashboard/send_messages.html", {'biz_messages': biz_messages})



def error_page(error_message):
    return HttpResponse(error_message)

@login_required
def admin_dashboard_send_message_detail(request, id):
    if request.user.groups.filter(name='sender').count() == 0:
        return error_page("למשתמש אין הרשאת שליחה לעסק")
    message = ContentSchedule.objects.get(id=id)
    if message.business != request.user.me.business:
        return error_page('אין לך הרשאה למשאב זה')
    
    if request.method == 'POST':
        is_sent = request.POST.get('is_whatsapp_sent', '')
        if is_sent == 'on':
            message.is_whatsapp_sent = True
        else:
            message.is_whatsapp_sent = False
        message.save()
        messages.add_message(request, messages.SUCCESS, 'הודעה עודכנה בהצלחה')
        action = request.POST.get('action')
        if action == 'save':
            return redirect('admin_dashboard_send_messages')
        elif action == 'save_and_continue_editing':
            return redirect('admin_dashboard_send_message_detail', id=message.id)
    return render(request, 'admin_dashboard/send_message_detail.html', {'message': message})