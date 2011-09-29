from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext
from django.contrib import admin

from django.http import HttpResponse
from django.core import serializers
from nani.admin import TranslatableAdmin

from .forms import EntryForm
from .models import Entry, Category
    
class EntryAdmin(TranslatableAdmin):
    """
        Admin for entry
    """
    date_hierarchy = 'pub_date'
    list_display = ('__unicode__', 'slug', 'category', 'is_published', 'pub_date')
    list_filter = ('is_published', 'category')
    search_fields = ['title', 'excerpt', 'content']
    #prepopulated_fields = {'slug': ('title',)} # doesn't work with Nani
    form = EntryForm

    actions = ['make_published', 'make_unpublished']

    fieldsets = ((None, {'fields': ('title', 'slug', 'category')}),
                 ('Entry', {'fields': ('excerpt', 'content')}),
                 ('Image', {'fields': ('image', 'alignment')}),
                 ('Publishing', {'fields': ('is_published', 'pub_date')}))

    save_as = True
    save_on_top = True
    
    def make_published(self, request, queryset):
        """
            Marks selected news items as published
        """
        rows_updated = queryset.update(is_published=True)
        self.message_user(request, ungettext('%(count)d newsitem was published', 
                                            '%(count)d newsitems where published', 
                                            rows_updated) % {'count': rows_updated})
    make_published.short_description = _('Publish selected news')

    def make_unpublished(self, request, queryset):
        """
            Marks selected news items as unpublished
        """
        rows_updated =queryset.update(is_published=False)
        self.message_user(request, ungettext('%(count)d newsitem was unpublished', 
                                            '%(count)d newsitems where unpublished', 
                                            rows_updated) % {'count': rows_updated})
    make_unpublished.short_description = _('Unpublish selected news')

admin.site.register(Entry, EntryAdmin)
admin.site.register(Category, TranslatableAdmin)
