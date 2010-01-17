import random

from django import template
from django.conf import settings

from epiweb.apps.banner.models import Image

register = template.Library()

@register.inclusion_tag('banner/image.html')
def banner_image(name=None):
    if name is None:
        objs = Image.objects
    else:
        objs = Image.objects.filter(category__name=name)

    ids = objs.values_list('id', flat=True)
    id = random.choice(ids)
    print ids

    image = Image.objects.get(pk=id)

    url = image.url
    if not url.startswith('http'):
        url = '/%s' % url
    path = '%s%s' % (settings.MEDIA_URL, str(image.image))
        
    return {'title': image.title,
            'url': url,
            'image': path}

