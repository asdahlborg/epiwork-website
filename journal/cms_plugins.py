from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from journal.models import LatestEntryPlugin, Entry
from journal import settings

class CMSLatestEntryPlugin(CMSPluginBase):
    """
        Plugin class for the latest news
    """
    model = LatestEntryPlugin
    name = _('Latest journal entries')
    render_template = "journal/latest.html"
    
    def render(self, context, instance, placeholder):
        """
            Render the latest news
        """
        categories = instance.category.all()
        if len(categories) > 0:
            query = map(lambda category: Q(category=category), 
                        categories)
            query = reduce(lambda a, b: a | b, query)
        else:
            query = Q()
        latest = Entry.published.filter(query)[:instance.limit]
        context.update({
            'title': instance.title,
            'instance': instance,
            'latest': latest,
            'placeholder': placeholder,
        })
        return context

if not settings.DISABLE_LATEST_ENTRIES_PLUGIN:
    plugin_pool.register_plugin(CMSLatestEntryPlugin)
