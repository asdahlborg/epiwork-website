from __future__ import absolute_import

from django.template import Library, Node
from django.contrib.sites.models import Site
from django.conf import settings

from ..models import SiteSettings

register = Library()

def make_do_current_site(f):
    def do_current_site(parser, token):
        contents = token.split_contents()
        assert len(contents) == 1, "%r tag requires a single argument" % contents[0]
        return CurrentSiteNode(f)
    return do_current_site

class CurrentSiteNode(Node):
    def __init__(self, f):
        self.f = f

    def render(self, context):
        site = Site.objects.get_current()
        return self.f(site, SiteSettings.get(site))

def do_if_logo(parser, token):
    nodelist = parser.parse(('endif_site_logo',))
    parser.delete_first_token() # delete 'endif_site_logo'

    parts = token.split_contents()

    if len(parts) != 1:
        raise TemplateSyntaxError("if_site_logo tag takes no arguments")

    return IfLogoNode(nodelist)

class IfLogoNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        return output if SiteSettings.get(Site.objects.get_current()).logo else ""

register.tag('site_name', make_do_current_site(lambda site, _: site.name))
register.tag('site_logo', make_do_current_site(lambda _, settings: settings.logo.url if settings.logo else ""))
register.tag('if_site_logo', do_if_logo)

def do_google_analytics(parser, token):
    contents = token.split_contents()
    assert len(contents) == 1, "%r tag has no arguments" % contents[0]
    return GoogleAnalyticsNode()

class GoogleAnalyticsNode(Node):
    def render(self, context):
        if not hasattr(settings, 'GOOGLE_ANALYTICS_ACCOUNT') or settings.GOOGLE_ANALYTICS_ACCOUNT is None:
            return ""

        return """<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', '%s']);
  _gaq.push(['_setDomainName', 'none']);
  _gaq.push(['_setAllowLinker', true]);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>""" % settings.GOOGLE_ANALYTICS_ACCOUNT

register.tag('google_analytics', do_google_analytics)
