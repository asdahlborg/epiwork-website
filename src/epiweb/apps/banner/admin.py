from django.contrib import admin

from epiweb.apps.banner.models import Image, Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'updated')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Image, ImageAdmin)

