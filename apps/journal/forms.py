from django import forms
from django.conf import settings

from nani.forms import TranslatableModelForm

from cms.plugin_pool import plugin_pool
from cms.plugins.text.settings import USE_TINYMCE
from .widgets.wymeditor_widget import WYMEditor


from .models import Entry

class EntryForm(TranslatableModelForm):
    class Meta:
        model = Entry
        
    def _get_widget(self):
        plugins = plugin_pool.get_text_enabled_plugins(placeholder=None, page=None)
        if USE_TINYMCE and "tinymce" in settings.INSTALLED_APPS:
            from journal.widgets.tinymce_widget import TinyMCEEditor
            return TinyMCEEditor(installed_plugins=plugins)
        else:
            return WYMEditor(installed_plugins=plugins)
        
        
    def __init__(self, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        widget = self._get_widget()
        self.fields['content'].widget = widget
        
