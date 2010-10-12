from django.template import Library, Node, TemplateSyntaxError
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe

from cms.utils import get_language_from_request
from cms.utils.moderator import get_page_queryset

register = Library()

@register.inclusion_tag('cms/dummy.html', takes_context=True)
def page_children(context, template="cms_extra/children.html"):
    context.update({'template': template})

    site = Site.objects.get_current()
    request = context['request']
    current = request.current_page
    if current == 'dummy':
        return context

    page_queryset = get_page_queryset(request)

    filters = {'in_navigation':True, 
               'lft__gt':current.lft, 
               'rght__lt':current.rght, 
               'tree_id':current.tree_id, 
               'level':current.level+2,
               'site':site}
    gc = page_queryset.published().filter(**filters)
    parent_ids = [c.parent_id for c in gc] 

    filters = {'parent': current,
               'in_navigation': True}
    descendant = list(page_queryset.published().filter(**filters))
    children = [item for item in descendant if item.id not in parent_ids]

    context.update({'children': children})
    return context

@register.inclusion_tag('cms/dummy.html', takes_context=True)
def page_subfolders(context, template='cms_extra/subfolders.html'):
    context.update({'template': template})

    site = Site.objects.get_current()
    request = context['request']
    current = request.current_page
    if current == 'dummy':
        return context

    page_queryset = get_page_queryset(request)

    filters = {'in_navigation':True, 
              'lft__gt':current.lft, 
              'rght__lt':current.rght, 
              'tree_id':current.tree_id, 
              'level':current.level+2,
              'site':site}
    gc = page_queryset.published().filter(**filters)
    parent_ids = [c.parent_id for c in gc] 

    filters = {'parent': current,
               'in_navigation': True}
    descendant = list(page_queryset.published().filter(**filters))
    subfolders = [item for item in descendant if item.id in parent_ids]

    context.update({'subfolders': subfolders})
    return context

@register.inclusion_tag('cms/dummy.html', takes_context=True)
def page_parents(context, template="cms_extra/parents.html"):
    context.update({'template': template})

    site = Site.objects.get_current()
    request = context['request']
    current = request.current_page
    if current == 'dummy':
        return context

    page_queryset = get_page_queryset(request)
    filters = {'tree_id': current.tree_id,
               'level__lt': current.level}
    gc = page_queryset.published().filter(**filters)
    all_parents = dict([(p.id, p) for p in gc])

    parents = []
    while current.level > 0:
        current = all_parents[current.parent_id]
        parents.append(current)
    parents = list(reversed(parents))

    context.update({'parents': parents})
    return context

@register.filter
def first_plugin(page, placeholder=None):
    try:
        if placeholder is None:
            plugins = page.cmsplugin_set.all().order_by('position')
        else:
            plugins = page.cmsplugin_set.filter(placeholder=placeholder)\
                                        .order_by('position')
        if len(plugins) > 0:
            return mark_safe(plugins[0].render_plugin())
        else:
            return ''
    except IndexError:
        return ''

class HiddenPlaceholderNode(Node):
    def __init__(self, name):
        self.name = "".join(name.lower().split('"'))

    def render(self, context):
        if context.get('display_placeholder_names_only'):
            return '<!-- PlaceholderNode: %s -->' % self.name
        return ''

def do_hidden_placeholder(parser, token):
    error_string = '%r tag requires 1 argument'
    try:
        bits = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError(error_string)
    return HiddenPlaceholderNode(bits[1])

register.tag('hidden_placeholder', do_hidden_placeholder)

