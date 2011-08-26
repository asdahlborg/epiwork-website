from __future__ import absolute_import

from django.template import Library, Node
from django.conf import settings

register = Library()

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
