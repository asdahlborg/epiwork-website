from cms.plugin_base import CMSPluginBase
from cms.models import CMSPlugin
from cms.plugin_pool import plugin_pool
from cms.utils.helpers import reversion_register
from django.db import models

from epiweb.apps.banner.models import Category

class BannerCategory(CMSPlugin):
    category = models.ManyToManyField(Category, null=True, blank=True)

reversion_register(BannerCategory)

class BannerPlugin(CMSPluginBase):
    model = BannerCategory
    name = "Banner"
    render_template = "banner/cms_plugins.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        categories = [cat.name for cat in instance.category.all()]

        context.update({
            'categories': categories
        })
        return context

plugin_pool.register_plugin(BannerPlugin)

