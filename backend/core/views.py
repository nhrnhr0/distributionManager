from django.shortcuts import render, redirect
from models.models import Business, Category, ContentSchedule, BusinessQR, LeadsClicks, CategoriesClicks
# Create your views here.
def busines_join(request, business_slug):
    biz = Business.objects.get(slug=business_slug)
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
        click = CategoriesClicks(business=biz, category=category, qr=qr_obj)
        click.save()
        pass
    else:
        # add click
        click = CategoriesClicks(business=biz, category=category,group_type=CategoriesClicks.CATEGORY_GROUP_TELEGRAM)
        click.save()
    
    link = category.open_telegram_url.get_link()
    # redirect to telegram link
    return redirect(link)


def send_scheduled_telegram_messages():
    
    for message in ContentSchedule.objects.all():
        if message.should_send_telegram():
            message.send_telgram_message()
    pass