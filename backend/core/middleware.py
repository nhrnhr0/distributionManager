from django.urls import resolve, Resolver404
from django.utils.translation import gettext as _

BREADCRUMBS_TRANSLATION = {
    'dashboard_index': _('Dashboard'),
    'dashboard_leads_in': _('Leads In'),
    'dashboard_leads_out': _('Leads Out'),
    'dashboard_messages': _('Messages'),
    'message_new': _('New Message'),
    'message_edit': _('Edit Message'),
    'message_send': _('Send Message'),
    'message_edit_send': _('Edit Send Message'),
    'business_join': _('Join Business'),
    'business_join_whatsapp': _('Join Business Whatsapp'),
    'business_join_telegram': _('Join Business Telegram'),
    'redirector': _('Redirector'),
}


# middleware to add breadcrumbs to the context
class BreadcrumbsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        breadcrumbs = []
        if request.path != '/':
            path = request.path.split('/')
            # for each part, we check for resolve
            curr = ''
            for i, part in enumerate(path):
                try:
                    curr += part + '/'
                    resolved = resolve(curr)
                    breadcrumbs.append({'name': resolved.url_name, 'url': curr, 'label': BREADCRUMBS_TRANSLATION.get(resolved.url_name, resolved.url_name)})
                except Resolver404:
                    pass
        request.breadcrumbs = breadcrumbs
        response = self.get_response(request)
        return response
    