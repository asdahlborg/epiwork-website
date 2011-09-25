from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from django.conf.urls.defaults import *
from apps.survey.api.handlers import ( GetUserProfile,
                                       GetReportSurvey,
                                       GetImage,
                                       Report,
                                       GetLanguage,
                                       GetStatsHeaders,
                                       GetStatistic,
                                     )
from re import match

# htttp basic authentication

auth = HttpBasicAuthentication(realm="EIP")
ad = { 'authentication': auth }

# Perform some introspection on the handlers in order to build the urlpatterns.

resources = [ [GetUserProfile, 'uid'],
              [GetReportSurvey, 'language'],
              [GetImage, 'uid', 'image_type'],
              [Report, 'uid', 'reports'],
              [GetLanguage],
              [GetStatsHeaders, 'language'],
              [GetStatistic, 'lang', 'id', 'uid'],
            ]

def stringify(c):
    "Returns string name for class."
    m = match("<.*\.([^>]+)'>", str(c))
    if m:
        return m.group(1)
    else:
        return ''

q = [url(r'^%s' % stringify(s[0]) + 
         reduce(lambda acc,i: r'/(?P<%s>[^/]+)' % str(i) + acc, s[1:], ''),
         Resource(handler=s[0], **ad)
         #, {'emitter_format': 'json'}
         )
     for s in resources]

r = [url(r'^%s' % stringify(s[0]), Resource(handler=s[0], **ad)
         #, {'emitter_format': 'json'}
         )
     for s in resources]

p = q + r
p.insert(0, '')

urlpatterns = patterns(*p)
