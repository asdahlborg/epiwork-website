import datetime

from haystack.indexes import *
from haystack import site

from django.utils.html import strip_tags

from cms.models import Page, Placeholder

class PageIndex(SearchIndex):
    text = CharField(document=True)
    summary = CharField()

    def prepare(self, obj):
        self.prepared_data = super(PageIndex, self).prepare(obj)
        placeholders = obj.placeholders.all()
        text = ''

        for placeholder in placeholders:
            for plugin in placeholder.get_plugins_list():
                instance, _ = plugin.get_plugin_instance()
                if hasattr(instance, 'search_fields'):
                    for field in instance.search_fields:
                        if field == 'snippet__html':
                            continue
                        text += getattr(instance, field) + " "

            self.prepared_data['text'] = text
            self.prepared_data['summary'] = strip_tags(text.replace(">", "> "))

        return self.prepared_data

    def index_queryset(self):
        return Page.objects.published()

site.register(Page, PageIndex)
