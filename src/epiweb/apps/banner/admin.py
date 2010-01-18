from django.contrib import admin

from epiweb.apps.banner.models import Image, Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

def categories(obj):
    cats = map(lambda x: x.name, obj.category.all())
    if len(cats) > 4:
        cats = cats[0:3] + ['...']
    return ', '.join(cats)
categories.short_description = 'Categories'

class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'active', 'url', categories)
    fieldsets = (
        (None, {
            'fields': ('title', 'image', 'url', 'category'),
        }),
    )
    list_editable = ('active',)
    list_select_related = True

admin.site.register(Category, CategoryAdmin)
admin.site.register(Image, ImageAdmin)

