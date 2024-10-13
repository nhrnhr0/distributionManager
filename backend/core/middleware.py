from django.urls import resolve, Resolver404
from django.utils.translation import gettext as _
import json
from django.http import HttpResponse

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
    




class NonHtmlDebugToolbarMiddleware(object):
    """
    The Django Debug Toolbar usually only works for views that return HTML.
    This middleware wraps any JSON response in HTML if the request
    has a 'debug' query parameter (e.g. http://localhost/foo?debug)

    adapted from:
    https://gist.github.com/fabiosussetto/c534d84cbbf7ab60b025
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.GET.get('debug', None) is not None:
            if response['Content-Type'] == 'application/json':
                content = json.dumps(json.loads(response.content), sort_keys=True, indent=2)
                response = HttpResponse(u'<html><body><pre>{}</pre></body></html>'.format(content))

        return response