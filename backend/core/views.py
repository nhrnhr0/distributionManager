from django.shortcuts import render, redirect
from models.models import Business, Category, BusinessQR, LeadsClicks, CategoriesClicks, MessageLink, MessageLinkClick, Call
from counting.models import CallsResponsesCount
from django.http import JsonResponse
from .decoretors import admin_required
import json
import re
import openai

@admin_required
def apply_ai_correction_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        original_message = data['message']
        corrections = data['correction']
    
    
        prompt = f"""
הודעה מקורית ואל תציג טקסט של הודעה מתוקנת:
{original_message}

הערות לתיקון:
{corrections}
"""
        response = fetch_ai_response(prompt, "תקן את ההודעה הבאה בהתאם להערות שהתקבלו. שים לב לתקן רק את החלקים המבוקשים.")
        return JsonResponse({'status': 'success', 'message': 'AI message generated successfully', 'msg': response})
    pass

@admin_required
def generate_ai_message_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_metadata = data.get('product_metadata', '')
        product_name = data.get('product_name', '')
        description = data.get('description', '')
        price = data.get('price', '')
        coupon_code = data.get('coupon_code', '')
        product_links = data.get('product_links', [])
        categories = data.get('categories', [])
        business = data.get('business', '')
        phone_number = Business.objects.get(id=business).phone
        biz = request.user.profile.biz
        system_prompt = biz.get_ai_system_prompt()
        prompt = make_ai_template(product_metadata, product_name, description, price, coupon_code, product_links, categories, phone_number)
        print(prompt)
        #print(system_prompt)
        
        msg = fetch_ai_response(prompt, system_prompt)
        
        return JsonResponse({'status': 'success', 'message': 'AI message generated successfully', 'msg': msg})

def fetch_ai_response(prompt, system_message):
    # Message Generation
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.3
        )
        generated_message = response.choices[0].message['content'].strip()
        # generated_message = re.sub(
        #     r'\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)', r'\2', generated_message)
        return generated_message

def make_ai_template(product_metadata, product_name, description, price, coupon, product_links, categories, phone_number):
    categories_objs = Category.objects.filter(id__in=[c['category'] for c in categories])
    categories_names = []
    for category in categories_objs:
        categories_names.append(category.name)
    
    product_links_template = ""
    for link in product_links:
        product_links_template += f"[link:{link['description']}] "

    coupon_text = f"✅ קוד קופון: {coupon}" if coupon else ""
    
    prompt_message = f"""
פרטי המוצר:
- מידע נוסף: {product_metadata}
- שם המוצר: {product_name}
- תיאור: {description}
- מחיר: {(price + '₪') if price else ''}
- קישורים להזמנה: {product_links_template}
- קוד קופון: {coupon_text if coupon else ''}
- מספר טלפון: {phone_number}
- קטגוריות: {','.join(categories_names)}
"""
    return prompt_message
    pass
def calls_webhook(request):
    caller_id = request.GET.get('caller_number_friendly', '')
    call_status = request.GET.get('type', '')
    call_length = request.GET.get('time_duration_seconds', 0)
    time_started = request.GET.get('time_started', '')
    own_number_friendly = request.GET.get('own_number_friendly', '')
    if not caller_id or not call_status or not time_started or not own_number_friendly:
        return JsonResponse({'status': 'error', 'message': 'Missing required parameters'})
    # Create a new Call object
    call_obj = Call.objects.create(
        caller_id=caller_id,
        call_status=call_status,
        call_length=int(call_length) if call_length else 0,
        time_started=time_started,
        own_number_friendly=own_number_friendly
    )
    
    # find the biz based on own_number_friendly is equal to biz.phone
    bizs = Business.objects.filter(phone=own_number_friendly)
    if bizs.exists():
        biz = bizs.first()
        call_tracker = CallsResponsesCount.objects.create(business=biz,count=1, rel=call_obj)
        call_tracker.save()

    # Return a JSON response to confirm successful storage
    return JsonResponse({'status': 'success', 'message': 'Call data stored successfully'})
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
    referrer = request.META.get('HTTP_REFERER')
    if link:
        # add click
        
        click = MessageLinkClick(
            msg=link.message,
            category=category,
            link=link,
            group_type=group_type,
            ip=ip,
            user_agent=user_agent,
            referrer=referrer)
        click.save()
        pass
    
    
        return redirect(link.url, permanent=False)

# Create your views here.
def busines_join(request, business_slug):
    biz = Business.objects.prefetch_related('categories__open_whatsapp_url','categories__open_telegram_url').get(slug=business_slug)
    campain_source_code = request.GET.get('c')
    qr_obj = BusinessQR.objects.filter(qr_code=campain_source_code).first()
    referrer = request.META.get('HTTP_REFERER')
    if qr_obj:
        # add click
        click = LeadsClicks(business=biz, qr=qr_obj, referrer=referrer)
        click.save()
        pass
    else:
        # add click
        click = LeadsClicks(business=biz, referrer=referrer)
        click.save()
        pass
    return render(request, 'core/join.html', {'biz': biz})


def busines_join_whatsapp_link(request, business_slug, category_slug):
    biz = Business.objects.get(slug=business_slug)
    category = Category.objects.get(slug=category_slug, business=biz)
    
    qr_obj = BusinessQR.objects.filter(qr_code=request.GET.get('c')).first()
    referrer = request.META.get('HTTP_REFERER')

    if qr_obj:
        # add click
        click = CategoriesClicks(business=biz, category=category, qr=qr_obj,group_type=CategoriesClicks.CATEGORY_GROUP_WHATSAPP, referrer=referrer)
        click.save()
        pass
    else:
        # add click
        click = CategoriesClicks(business=biz, category=category,group_type=CategoriesClicks.CATEGORY_GROUP_WHATSAPP, referrer=referrer)
        click.save()
    
    link = category.open_whatsapp_url.get_link()
    # redirect to whatsapp link
    return redirect(link)

def busines_join_telegram_link(request, business_slug, category_slug):
    biz = Business.objects.get(slug=business_slug)
    category = Category.objects.get(slug=category_slug, business=biz)
    
    qr_obj = BusinessQR.objects.filter(qr_code=request.GET.get('c')).first()
    referrer = request.META.get('HTTP_REFERER')
    
    if qr_obj:
        # add click
        click = CategoriesClicks(business=biz, category=category, qr=qr_obj,group_type=CategoriesClicks.CATEGORY_GROUP_TELEGRAM, referrer=referrer)
        click.save()
        pass
    else:
        # add click
        click = CategoriesClicks(business=biz, category=category,group_type=CategoriesClicks.CATEGORY_GROUP_TELEGRAM, referrer=referrer)
        click.save()
    
    link = category.open_telegram_url.get_link()
    # redirect to telegram link
    return redirect(link)
