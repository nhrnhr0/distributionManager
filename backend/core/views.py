from django.shortcuts import render, redirect
from models.models import Business, Category
# Create your views here.
def busines_join(request, business_slug):
    biz = Business.objects.get(slug=business_slug)
    return render(request, 'core/join.html', {'biz': biz})


def busines_join_whatsapp_link(request, business_slug, category_slug):
    biz = Business.objects.get(slug=business_slug)
    category = Category.objects.get(slug=category_slug, business=biz)
    link = category.open_whatsapp_url
    # redirect to whatsapp link
    return redirect(link)

def busines_join_telegram_link(request, business_slug, category_slug):
    biz = Business.objects.get(slug=business_slug)
    category = Category.objects.get(slug=category_slug, business=biz)
    link = category.open_telegram_url
    # redirect to telegram link
    return redirect(link)