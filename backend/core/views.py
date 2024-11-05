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
        
        [prompt, system_prompt] = make_ai_template(product_metadata, product_name, description, price, coupon_code, product_links, categories, phone_number)
        print(prompt)
        print(system_prompt)
        
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
    category_tones = {} # map category name to tone
    category_example_templates = {} # map category name to template
    product_categories = []
    for category in categories_objs:
        category_tones[category.name] = category.ai_message_tone
        category_example_templates[category.name] = category.ai_message_example
        product_categories.append(category.name)
    
    
    product_links_template = ""
    for link in product_links:
        product_links_template += f"[link:{link['description']}]"
    
    tones = [category_tones.get(category, "ניטרלי וברור") for category in product_categories]
    
    templates = [category_example_templates.get(category, "{product_name} – פרטים נוספים במחיר של {price} ש\"ח") for category in product_categories]
    # tones ['מקצועי ומכוון לתועלת', None]
    # templates ['🔋 {product_name} – כלי הכרחי לחירום. מוצר אמין במחיר של {price} ש\\"ח בלבד!', None]
    # remove nones
    tones = [tone for tone in tones if tone]
    templates = [template for template in templates if template]

    # Prepare coupon text conditionally
    coupon_text = f"✅ קוד קופון: {coupon}" if coupon else ""
    join_group_link = 'gm.bizbiz.co.il/join/ג-חיון/?c=0fa45f'

    # Define greeting based on metadata
    greetings_map = {
        "בוקר": "בוקר טוב 🌞",
        "ערב": "ערב טוב 🌇",
        "לילה": "לילה טוב 🌙",
        "צהריים": "צהריים טובים ☀️"
    }
    greeting_in_message = next(
        (greetings_map[g] for g in greetings_map if g in product_metadata), ""
    )

    # Concise Prompt for Professional, Inviting Message
    prompt = f"""
צור הודעת מכירה בסגנון {', '.join(tones)} עבור מוצר בקטגוריית {', '.join(product_categories)}. ההודעה צריכה להיות קצרה, מושכת,
וברורה,ומבוססת על פרטי המידע שסופקו – אך נכתבת מחדש באופן יצירתי כך שלא תשכפל את התיאור שהוזן,
אלא תציג אותו במילים חדשות.
במידה ולא הוכנס מידע על המחיר או קופון אל תכליל מחיר או קופון שלא יהיה משהו שיקרי. תתייחס כמו שצריך לאינפוטים ולא להמציא שום דבר.
אם משתמשים ב {greeting_in_message} תוסיף את זה בצורה מכירתית בעזרת פרומפט
בנוסף חשוב לי שיהיה  אימוג'ים מתאימים להודעה.

מבנה ההודעה:
1. פתיחה קלילה ומזמינה, שמסבירה את יתרונות המוצר מבלי לחזור במדויק על התיאור שסופק.
2. תיאור ייחודי וקצר של המוצר, המדגיש את הערך העיקרי עבור הלקוח (כמו נוחות, הגנה, כיף).
3. ציון ברור של המחיר כולל מע"מ, כך שיהיה בולט ומשתלם.
4. קריאה לפעולה להזמנה עם קישור לרכישה.
5. פנייה שירותית לסיום עם מספר טלפון ליצירת קשר, בסגנון כמו "לשירותכם", "נשמח לעזור" או "לייעוץ והכוונה".

פרטי המוצר:
- שם המוצר: {product_name}
- תיאור: {description}
- מחיר: {price if price else ''}
- קישורים להזמנה: {product_links_template}
- קוד קופון: {coupon_text if coupon else ''}
- קישור להצטרפות לעוד קבוצות שלנו: {join_group_link}
- מספר טלפון: {phone_number}

תבניות לדוגמה להודעות:
"""
    # הוספת כל תבנית עם הפרטים הנדרשים לכל קטגוריה שנבחרה
    for template in templates:
        prompt += f"\n{template.format(product_name=product_name, price=price)}"
        # Hebrew system message
    system_message = f"""
אתה עוזר שיווקי דובר עברית, המתמחה בכתיבת הודעות מכירה קצרות וברורות, בעברית תקינה וללא שגיאות כתיב.
השתמש רק במילים יומיומיות וברורות, והימנע ממילים נדירות או יוצאות דופן.
הודעות אלו צריכות להיות מקצועיות, מזמינות וממוקדות בפרטים שסופקו בלבד.
הקפד על ירידת שורה אחת בלבד
דוגמה להודעה במבנה הנדרש עבור קטגוריות {', '.join(product_categories)}:
"""

    for template in templates:
        system_message += f"\n{template.format(product_name=product_name, price=price)}"

    return [prompt, system_message]
    pass
def calls_webhook(request):
    caller_id = request.GET.get('caller_number_friendly', '')
    call_status = request.GET.get('type', '')
    call_length = request.GET.get('time_duration_seconds', 0)
    time_started = request.GET.get('time_started', '')
    own_number_friendly = request.GET.get('own_number_friendly', '')
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