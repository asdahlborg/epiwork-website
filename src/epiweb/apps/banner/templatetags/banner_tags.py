import random

from django import template
from django.db.models import Q
from django.conf import settings
from django.utils.safestring import SafeUnicode

from epiweb.apps.banner.models import Image

register = template.Library()

@register.inclusion_tag('banner/image.html')
def banner_image(names=[]):
    if type(names) == str or isinstance(names, SafeUnicode):
        names = names.split(',')
    
    if not names:
        objs = Image.objects
    else:
        query = map(lambda name: Q(category__name=name), names)
        query = reduce(lambda a, b: a | b, query)
        objs = Image.objects.filter(query)

    banner = None

    ids = objs.values_list('id', flat=True).distinct()
    if len(ids) > 0:
        id = random.choice(ids)

        image = Image.objects.get(pk=id)

        url = image.url
        if not url.startswith('http'):
            url = '/%s' % url
        path = '%s%s' % (settings.MEDIA_URL, str(image.image))

        banner = {}
        banner['title'] = image.title
        banner['url'] = url
        banner['image'] = path

    return {'banner': banner}

