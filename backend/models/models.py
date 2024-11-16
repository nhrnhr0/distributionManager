from typing import Iterable
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
import backend.settings as settings
import requests
import uuid
from django.utils.translation import gettext as _
import qrcode
import os
import requests
from io import BytesIO
from django.core.files import File
from core.utils import generate_small_uuid,generate_unique_uid


class Call(models.Model):
    caller_id = models.CharField(max_length=50, blank=True, null=True)
    call_status = models.CharField(max_length=50, blank=True, null=True)
    call_length = models.IntegerField(blank=True, null=True)
    time_started = models.CharField(max_length=50)
    own_number_friendly = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Call {self.caller_id} - Status: {self.call_status}"

    
class SysUser(models.Model):
    name = models.CharField(_("name"), max_length=100)
    user = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, related_name="me", verbose_name=_("user")
    )
    business = models.ForeignKey(
        "Business",
        on_delete=models.CASCADE,
        related_name="users",
        verbose_name=_("business"),
    )

    def __str__(self) -> str:
        return self.name


class Business(models.Model):
    name = models.CharField(_("name"), max_length=100)
    display_name = models.CharField(
        _("display name"), max_length=100, blank=True, null=True
    )
    slug = models.SlugField(_("slug"), max_length=100, unique=True, allow_unicode=True)
    header_image = models.ImageField(
        _("header image"), upload_to="businesses/", blank=True, null=True
    )
    footer_image = models.ImageField(
        _("footer image"), upload_to="businesses/", blank=True, null=True
    )
    description = models.TextField(
        _("description"), max_length=20000, blank=True, null=True
    )
    favicon = models.ImageField(
        _("favicon"), upload_to="businesses/", blank=True, null=True
    )
    phone = models.CharField(_('phone'), max_length=100, blank=True, null=True)
    telegram_fotter = models.CharField(_('telegram footer'), max_length=2500, blank=True, null=True)
    
    ai_system_prompt = models.CharField(_('AI message prompt'), max_length=10000, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return "/join/" + self.slug

    class Meta:
        verbose_name = _("business")
        verbose_name_plural = _("businesses")

        
        
    def get_ai_system_prompt(self):
        return self.ai_system_prompt or """
אתה עוזר שיווקי דובר עברית, המתמחה בכתיבת הודעות מכירה קצרות וברורות, בעברית תקינה וללא שגיאות כתיב.
השתמש רק במילים יומיומיות וברורות, והימנע ממילים נדירות או יוצאות דופן.
הודעות אלו צריכות להיות מקצועיות, מזמינות וממוקדות בפרטים שסופקו בלבד.

צור הודעת מכירה בסגנון ניטרלי וברור.
ההודעה צריכה להיות קצרה, מושכת, וברורה,ומבוססת על פרטי המידע שסופקו בלבד– אך נכתבת מחדש באופן יצירתי כך שלא תשכפל את התיאור שהוזן,
אלא תציג אותו במילים חדשות ומכירתיות.
במידה ולא הוכנס מידע על המחיר או קופון אל תכליל מחיר או קופון שלא יהיה משהו שיקרי. תתייחס כמו שצריך לקלט ולא להמציא שום דבר.
בנוסף חשוב לי שיהיה  אימוג'ים מתאימים להודעה.
קישור להצטרפות לעוד קבוצות שלנו חובה שיופיע בהודעה בתור טקסט רגיל שנראה ככה בדיוק: 'gm.bizbiz.co.il/join/ג-חיון/?c=0fa45f'
חשוב מאוד! אם קיימים "קישורים להזמנה" צריך להכיס אותם אחד לאחד כמו שהם מופיעים במקור, כלומר [link:מזהה הקישו]
מבנה ההודעה:
1. פתיחה קלילה ומזמינה, שמסבירה את יתרונות המוצר מבלי לחזור במדויק על התיאור שסופק.
2. תיאור ייחודי וקצר של המוצר, המדגיש את הערך העיקרי עבור הלקוח (כמו נוחות, הגנה, כיף).
3. ציון ברור של המחיר כולל מע"מ, כך שיהיה בולט ומשתלם.
4. קריאה לפעולה להזמנה עם קישור לרכישה.
5. פנייה שירותית לסיום עם מספר טלפון ליצירת קשר, בסגנון כמו "לשירותכם", "נשמח לעזור" או "לייעוץ והכוונה".
מתחת מופיע פרטי ההודעה, המידע צריך להיות מוצג בהודעה בצורה מדוייקת וברורה, תתעלם ממידע ריק
"""

class BusinessQRCategories(models.Model):
    name = models.CharField(_("name"), max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("business QR category")
        verbose_name_plural = _("business QR categories")


# after busines is created/updated, we need to make sure each whatsapp and telegram group in the categories has initialized count
@receiver(
    post_save,
    sender=Business,
    dispatch_uid="init_whatsapp_group_members_first_count_for_all_categories",
)
def init_whatsapp_group_members_first_count_for_all_categories(
    sender, instance, **kwargs
):
    for category in instance.categories.all():
        for group in category.all_whatsapp_urls.all():
            group.init_whatsapp_group_members_first_count()
        for group in category.all_telegram_urls.all():
            group.init_telegram_group_members_first_count()


class LeadsClicks(models.Model):
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="leads_clicks",
        verbose_name=_("business"),
    )
    qr = models.ForeignKey(
        "BusinessQR",
        on_delete=models.CASCADE,
        related_name="leads_clicks",
        null=True,
        blank=True,
        verbose_name=_("QR"),
    )
referrer = models.CharField(_('referrer'), max_length=1000, blank=True, null=True)
    class Meta:
        verbose_name = _("leads click")
        verbose_name_plural = _("leads clicks")


class CategoriesClicks(models.Model):
    CATEGORY_GROUP = (
        ("whatsapp", "whatsapp"),
        ("telegram", "telegram"),
    )
    CATEGORY_GROUP_WHATSAPP = "whatsapp"
    CATEGORY_GROUP_TELEGRAM = "telegram"

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="categories_clicks",
        verbose_name=_("business"),
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="categories_clicks",
        verbose_name=_("category"),
    )
    qr = models.ForeignKey(
        "BusinessQR",
        on_delete=models.CASCADE,
        related_name="categories_clicks",
        null=True,
        blank=True,
        verbose_name=_("QR"),
    )
    group_type = models.CharField(
        _("group type"),
        max_length=100,
        choices=CATEGORY_GROUP,
        default=CATEGORY_GROUP_WHATSAPP,
    )
    referrer = models.CharField(_('referrer'), max_length=1000, blank=True, null=True)
    class Meta:
        verbose_name = _("categories click")
        verbose_name_plural = _("categories clicks")


class BusinessQR(models.Model):
    name = models.CharField(_("name"), max_length=100)
    category = models.ForeignKey(
        BusinessQRCategories,
        on_delete=models.CASCADE,
        related_name="qrs",
        verbose_name=_("category"),
    )
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="qrs",
        verbose_name=_("business"),
    )
    qr_code = models.CharField(
        _("QR code"),
        max_length=100,
        default=generate_small_uuid,
        unique=True,
        editable=False,
    )
    qr_img = models.ImageField(_("QR image"), upload_to="qrs/", blank=True, null=True)
    the_order = models.PositiveIntegerField(_("order"), default=0)

    class Meta:
        unique_together = ("name", "business", "category")
        verbose_name = _("business QR")
        verbose_name_plural = _("business QRs")
        ordering = [
            "the_order",
        ]

    def __str__(self) -> str:
        return self.category.name + " - " + self.name

    def get_link(self):
        if self.qr_code:
            return (
                settings.BACKEND_DOMAIN
                + "/join/"
                + self.business.slug
                + "/?c="
                + str(self.qr_code)
            )

    def html_qr_img(self):
        if self.qr_img:
            return mark_safe(f'<img src="{self.qr_img.url}" width="50" height="50" />')
        return _("No Image")

    html_qr_img.short_description = _("QR Image")

    def save(self):
        if not self.qr_img and self.qr_code:
            link = self.get_link()
            if link:
                qr_code_img = qrcode.make(link)
                img_io = BytesIO()
                qr_code_img.save(img_io, format="PNG")
                img_io.seek(0)
                filename = f"{self.qr_code}.png"
                self.qr_img.save(filename, File(img_io), save=False)
        return super().save()

    def get_html_link(self):
        return mark_safe(f'<a href="{self.get_link()}">{self.get_link()}</a>')

    get_html_link.short_description = _("Link")


class WhatsappGroup(models.Model):
    name = models.CharField(_("name"), max_length=120, blank=True, null=True)
    chat_id = models.CharField(_("chat ID"), max_length=120)
    # last_members_count = models.PositiveIntegerField(_('last members count'), default=0)
    # last_members_check = models.DateTimeField(_('last members check'), blank=True, null=True)

    def get_link(self):
        return "https://chat.whatsapp.com/" + self.chat_id

    def save(self):
        if self.chat_id.startswith("https://chat.whatsapp.com/"):
            self.chat_id = self.chat_id.replace("https://chat.whatsapp.com/", "")
        return super().save()

    def __str__(self) -> str:
        return (
            self.name
            + " - ("
            + ("".join([c.name for c in self.whatsapp_categories.all()]))
            + ")"
        )

    class Meta:
        verbose_name = _("WhatsApp group")
        verbose_name_plural = _("WhatsApp groups")

    def init_whatsapp_group_members_first_count(self):
        from counting.models import WhatsappGroupSizeCount, DaylyGroupSizeCount

        if not self.whatsapp_categories.first():
            return
        if WhatsappGroupSizeCount.objects.filter(group=self).exists():
            return
        # create new WhatsappGroupSizeCount and add it to the last session of this business
        session = DaylyGroupSizeCount.objects.filter(
            business=self.whatsapp_categories.first().business
        ).first()
        if not session:
            session = DaylyGroupSizeCount.objects.create(
                business=self.whatsapp_categories.first().business
            )
        WhatsappGroupSizeCount.objects.create(group=self, count=1, session=session)


# after a whatsapp group is created/updated, we need to make sure we have at least one manual count of the members
@receiver(
    post_save,
    sender=WhatsappGroup,
    dispatch_uid="init_whatsapp_group_members_first_count",
)
def init_whatsapp_group_members_first_count(sender, instance, **kwargs):
    instance.init_whatsapp_group_members_first_count()


class TelegramGroup(models.Model):
    name = models.CharField(_("name"), max_length=120, blank=True, null=True)
    chat_id = models.CharField(_("chat ID"), max_length=120)
    # last_members_count = models.PositiveIntegerField(_('last members count'), default=0)
    # last_members_check = models.DateTimeField(_('last members check'), blank=True, null=True)

    def get_link(self):
        return "https://t.me/" + self.chat_id

    def save(self):
        if self.chat_id.startswith("https://t.me/"):
            self.chat_id = self.chat_id.replace("https://t.me/", "")
        return super().save()

    def __str__(self) -> str:
        return (
            self.name
            + " - ("
            + ("".join([c.name for c in self.telegram_categories.all()]))
            + ")"
        )

    class Meta:
        verbose_name = _("Telegram group")
        verbose_name_plural = _("Telegram groups")

    def init_telegram_group_members_first_count(self):
        from counting.models import TelegramGroupSizeCount, DaylyGroupSizeCount

        if not self.telegram_categories.first():
            return
        if TelegramGroupSizeCount.objects.filter(group=self).exists():
            return
        # create new TelegramGroupSizeCount and add it to the last session of this business
        session = DaylyGroupSizeCount.objects.filter(
            business=self.telegram_categories.first().business
        ).first()
        if not session:
            session = DaylyGroupSizeCount.objects.create(
                business=self.telegram_categories.first().business
            )
        TelegramGroupSizeCount.objects.create(group=self, count=1, session=session)


def init_telegram_group_members_first_count(sender, instance, **kwargs):
    instance.init_telegram_group_members_first_count()


class Category(models.Model):
    uid = models.CharField(
        _("uid"),
        max_length=100,
        default=generate_unique_uid,
        editable=False,
        unique=True,
    )
    icon = models.ImageField(_("icon"), upload_to="categories/", blank=True, null=True)
    name = models.CharField(_("name"), max_length=100)
    slug = models.SlugField(_("slug"), max_length=100, allow_unicode=True)
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name=_("business"),
    )
    open_whatsapp_url = models.ForeignKey(
        to=WhatsappGroup,
        on_delete=models.SET_NULL,
        related_name="open_whatsapp_categories",
        null=True,
        blank=True,
        verbose_name=_("open WhatsApp URL"),
    )
    open_telegram_url = models.ForeignKey(
        to=TelegramGroup,
        on_delete=models.SET_NULL,
        related_name="open_telegram_categories",
        null=True,
        blank=True,
        verbose_name=_("open Telegram URL"),
    )
    all_whatsapp_urls = models.ManyToManyField(
        to=WhatsappGroup,
        related_name="whatsapp_categories",
        verbose_name=_("all WhatsApp URLs"),
    )
    all_telegram_urls = models.ManyToManyField(
        to=TelegramGroup,
        related_name="telegram_categories",
        verbose_name=_("all Telegram URLs"),
    )
    is_main_category = models.BooleanField(_('is main category'), default=False)
    the_order = models.PositiveIntegerField(_("order"), default=0)

    
    # ai_message_tone = models.CharField(_('AI message tone'), max_length=1000, blank=True, null=True)
    # ai_message_example = models.CharField(_('AI message example'), max_length=1000, blank=True, null=True)
    
    def __str__(self) -> str:
        return self.name + " - " + self.business.name

    class Meta:
        unique_together = ("slug", "business")
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["the_order"]

    def save(self):
        return super().save()

    def image_display(self):
        if self.icon:
            return mark_safe(f'<img src="{self.icon.url}" width="50" height="50" />')
        return _("No Image")

    image_display.short_description = _("Icon")


@receiver(post_save, sender=Category, dispatch_uid="update_open_groups")
def update_open_groups(sender, instance, **kwargs):
    updated = False
    if instance.open_whatsapp_url:
        if not instance.all_whatsapp_urls.filter(
            id=instance.open_whatsapp_url.id
        ).exists():
            instance.all_whatsapp_urls.add(instance.open_whatsapp_url)
            updated = True
    else:
        instance.open_whatsapp_url = instance.all_whatsapp_urls.first()
        if instance.open_whatsapp_url:
            updated = True

    if instance.open_telegram_url:
        if not instance.all_telegram_urls.filter(
            id=instance.open_telegram_url.id
        ).exists():
            instance.all_telegram_urls.add(instance.open_telegram_url)
            updated = True
    else:
        instance.open_telegram_url = instance.all_telegram_urls.first()
        if instance.open_telegram_url:
            updated = True
    if updated:
        instance.save()


# message we send, the admin can insert the message with links (inserted in the message placeholders) and categories the message need to be sent to, each with the date we need to send the message
class BizMessages(models.Model):
    uid = models.CharField(
        _("uid"),
        max_length=100,
        default=generate_small_uuid,
        unique=True,
        editable=False,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("business"),
        blank=True,
        null=True,
    )
    messageTxt = models.TextField(_("message"), max_length=20000)

    def __str__(self) -> str:
        return self.messageTxt

    class Meta:
        verbose_name = _("business message")
        verbose_name_plural = _("business messages")


class MessageCategory(models.Model):
    uid = models.CharField(
        _("uid"),
        max_length=100,
        default=generate_unique_uid,
        unique=True,
        editable=False,
    )
    message = models.ForeignKey(
        BizMessages,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name=_("message"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("category"),
        blank=True,
        null=True,
    )
    send_at = models.DateTimeField(
        _("send at"), blank=True, null=True
    )
    is_sent = models.BooleanField(_("is sent"), default=False)
    reminder_sent = models.BooleanField(_("reminder sent"), default=False)
    platform = models.CharField(
        max_length=20,
        choices=[("telegram", "Telegram"), ("whatsapp", "WhatsApp")],
        default="telegram",
    )

    class Meta:
        verbose_name = _("message category")
        verbose_name_plural = _("message categories")

    def get_generated_message_whatsapp(self):
        message = self.message.messageTxt
        DMN = settings.BACKEND_DOMAIN.replace("http://", "").replace("https://", "")
        for link in self.message.links.all():
            # replace [link:<description>] with redirect url /r/?c=<category_uid>&m=<message_uid>&l=<link_uid>
            new_link = (
                settings.BACKEND_DOMAIN
                + "/r/?c="
                + self.category.uid
                + "&l="
                + link.uid
                + "&t=w"
            )
            message = message.replace(f"[link:{link.description}]", new_link)
        return message

    def get_generated_message_telegram(self):
        message = self.message.messageTxt
        DMN = settings.BACKEND_DOMAIN.replace("http://", "").replace("https://", "")
        for link in self.message.links.all():
            # replace [link:<description>] with redirect url /r/?c=<category_uid>&m=<message_uid>&l=<link_uid>
            new_link = (
                settings.BACKEND_DOMAIN
                + "/r/?c="
                + self.category.uid
                + "&l="
                + link.uid
                + "&t=t"
            )
            message = message.replace(f"[link:{link.description}]", new_link)
        telegram_fotter = self.category.business.telegram_fotter
        if telegram_fotter:
            message += '\n' + telegram_fotter
        return message


# the links we insert in the message
class MessageLink(models.Model):
    uid = models.CharField(
        _("uid"),
        max_length=100,
        default=generate_unique_uid,
        editable=False,
        unique=True,
    )
    url = models.URLField(_("url"), max_length=2000)
    message = models.ForeignKey(
        BizMessages,
        on_delete=models.CASCADE,
        related_name="links",
        verbose_name=_("message"),
    )
    description = models.CharField(
        _("description"), max_length=100, blank=True, null=True
    )


# class MessageLinkTracker(models.Model):
#     uid = models.CharField(_('uid'), max_length=100, default=generate_small_uuid, unique=True, editable=False)
#     link = models.ForeignKey(MessageLink, on_delete=models.CASCADE, related_name='trackers', verbose_name=_('link'))
#     whatsapp_group = models.ForeignKey(WhatsappGroup, on_delete=models.CASCADE, related_name='trackers', verbose_name=_('group'))
#     telegram_group = models.ForeignKey(TelegramGroup, on_delete=models.CASCADE, related_name='trackers', verbose_name=_('group'))
#     group_type = models.CharField(_('group type'), max_length=100, choices=CategoriesClicks.CATEGORY_GROUP, default=CategoriesClicks.CATEGORY_GROUP_WHATSAPP)


class MessageLinkClick(models.Model):
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    msg = models.ForeignKey(
        BizMessages,
        on_delete=models.CASCADE,
        related_name="clicks",
        verbose_name=_("message"),
    )
    link = models.ForeignKey(
        MessageLink,
        on_delete=models.CASCADE,
        related_name="clicks",
        verbose_name=_("link"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="clicks",
        verbose_name=_("category"),
    )
    group_type = models.CharField(
        _("group type"),
        max_length=100,
        choices=CategoriesClicks.CATEGORY_GROUP,
        default=CategoriesClicks.CATEGORY_GROUP_WHATSAPP,
    )
    ip = models.GenericIPAddressField(_("IP"), blank=True, null=True)
    user_agent = models.TextField(_("user agent"), blank=True, null=True)
referrer = models.CharField(_('referrer'), max_length=1000, blank=True, null=True)