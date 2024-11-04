from django.shortcuts import render, redirect
from models.models import Business, Category, BusinessQR, LeadsClicks, CategoriesClicks, MessageLink, MessageLinkClick
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseBadRequest




def send_telegram_message(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if not message:
            return HttpResponseBadRequest("No message provided")  # Bad request if message is empty
        
        # Telegram API URL
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        
        # Payload
        payload = {
            'chat_id': settings.TELEGRAM_CHAT_ID,
            'text': message
        }
        
        # Send the request to Telegram
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return HttpResponse("Message sent successfully!")
        else:
            return HttpResponse(f"Failed to send message. Status code: {response.status_code}", status=response.status_code)
    
    return render(request, 'core/send_message.html')


def redirector(request):
    category_uid = request.GET.get('c')
    link_uid = request.GET.get('l')
    group_type = request.GET.get('t')
    
    link = MessageLink.objects.filter(uid=link_uid).first()
    category = Category.objects.filter(uid=category_uid).first()
    group_type = CategoriesClicks.CATEGORY_GROUP_WHATSAPP if group_type == 'w' else CategoriesClicks.CATEGORY_GROUP_TELEGRAM
    ip = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')
    if link:
        # add click
        
        click = MessageLinkClick(
            msg=link.message,
            category=category,
            link=link,
            group_type=group_type,
            ip=ip,
            user_agent=user_agent)
        click.save()
        pass
    
    
        return redirect(link.url, permanent=False)

# Create your views here.
def busines_join(request, business_slug):
    biz = Business.objects.prefetch_related('categories__open_whatsapp_url','categories__open_telegram_url').get(slug=business_slug)
    campain_source_code = request.GET.get('c')
    qr_obj = BusinessQR.objects.filter(qr_code=campain_source_code).first()
    if qr_obj:
        # add click
        click = LeadsClicks(business=biz, qr=qr_obj)
        click.save()
        pass
    else:
        # add click
        click = LeadsClicks(business=biz)
        click.save()
        pass
    return render(request, 'core/join.html', {'biz': biz})


def busines_join_whatsapp_link(request, business_slug, category_slug):
    biz = Business.objects.get(slug=business_slug)
    category = Category.objects.get(slug=category_slug, business=biz)
    
    qr_obj = BusinessQR.objects.filter(qr_code=request.GET.get('c')).first()
    if qr_obj:
        # add click
        click = CategoriesClicks(business=biz, category=category, qr=qr_obj)
        click.save()
        pass
    else:
        # add click
        click = CategoriesClicks(business=biz, category=category,group_type=CategoriesClicks.CATEGORY_GROUP_WHATSAPP)
        click.save()
    
    link = category.open_whatsapp_url.get_link()
    # redirect to whatsapp link
    return redirect(link)

def busines_join_telegram_link(request, business_slug, category_slug):
    biz = Business.objects.get(slug=business_slug)
    category = Category.objects.get(slug=category_slug, business=biz)
    
    qr_obj = BusinessQR.objects.filter(qr_code=request.GET.get('c')).first()
    if qr_obj:
        # add click
        click = CategoriesClicks(business=biz, category=category, qr=qr_obj,group_type=CategoriesClicks.CATEGORY_GROUP_TELEGRAM)
        click.save()
        pass
    else:
        # add click
        click = CategoriesClicks(business=biz, category=category,group_type=CategoriesClicks.CATEGORY_GROUP_TELEGRAM)
        click.save()
    
    link = category.open_telegram_url.get_link()
    # redirect to telegram link
    return redirect(link)
