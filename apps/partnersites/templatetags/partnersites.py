from __future__ import absolute_import
from django.template import Library, Node
from django.contrib.sites.models import Site

register = Library()

def do_current_site(parser, token):
    contents = token.split_contents()
    assert len(contents) == 1, "%r tag requires a single argument" % contents[0]
    return CurrentSiteNode()

class CurrentSiteNode(Node):
    def render(self, context):
        return Site.objects.get_current().name

register.tag('site_name', do_current_site)
