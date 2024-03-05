
from django import template
register = template.Library()

@register.simple_tag
def url_replace(request, field, value):
    d = request.GET.copy()
    d[field] = value
    return d.urlencode()

@register.simple_tag
def url_delete(request, field):
    d = request.GET.copy()
    try:
        del d[field]
    except KeyError:
        pass
    ret = d.urlencode()
    # if ret == '':
    #     return '?'
    return ret


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 