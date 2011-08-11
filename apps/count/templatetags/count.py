from __future__ import absolute_import

import urllib

from django.template import Library, Node
from django.contrib.sites.models import Site

register = Library()

FAKED = {
    'nl': '17952',
    'be': '4717',
    'uk': '703',
}

SOURCES = {
    'nl': 'http://www.grotegriepmeting.nl/count/counter/',
    'de': 'http://www.aktivgegengrippe.de/count/counter/',
    'at': 'http://www.aktivgegengrippe.at/count/counter/',
    'se': 'http://www.aktivgegengrippe.at/count/counter/',
    'uk': 'http://www.aktivgegengrippe.at/count/counter/',
    'it': 'http://www.influweb.it/count/counter',
    'pt': 'http://www.gripenet.pt/cgear/pt.php',
}

def do_member_count(parser, token):
    contents = token.split_contents()
    assert len(contents) == 2, "%r tag requires a single argument" % contents[0]
    country = contents[1]
    assert country[0] in ['"', "'"], "argument must be a string"
    country = country[1:-1]
    return MemberCountNode(country)

class MemberCountNode(Node):
    def __init__(self, country):
        self.country = country 

    def render(self, context):
        if self.country in FAKED:
            return FAKED[self.country]

        return urllib.urlopen(SOURCES[self.country]).read()

register.tag('member_count', do_member_count)

