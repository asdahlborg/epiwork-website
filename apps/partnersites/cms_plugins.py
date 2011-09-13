"""Strictly this is not 'partnersites' functionality, but rather 'cms_extensions', but a separate app also felt like overkill"""

from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cms.plugins.link.cms_plugins import LinkPlugin

class ExternalLinkPlugin(LinkPlugin):
    render_template = "cms/plugins/external_link.html"
    name = _("External link")

plugin_pool.register_plugin(ExternalLinkPlugin)
