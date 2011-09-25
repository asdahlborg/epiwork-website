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

resources = [ 
              (GetUserProfile, ('uid',)),
              (GetReportSurvey, ('language',)),
              (GetImage, ('uid', 'image_type',)),
              (Report, ('uid', 'reports',)),
              (GetLanguage, ()),
              (GetStatsHeaders, ('language',)),
              (GetStatistic, ('lang', 'id', 'uid',)),
            ]

q = [url(r'^%s' % handler.__name__ + 
         reduce(lambda acc,i: r'/(?P<%s>[^/]+)' % str(i) + acc, attrs, ''),
         Resource(handler=handler, **ad)
         #, {'emitter_format': 'json'}
         )
     for handler, attrs in resources]

r = [url(r'^%s' % handler.__name__, Resource(handler=handler, **ad)
         #, {'emitter_format': 'json'}
         )
     for handler, attr in resources]

p = q + r
p.insert(0, '')

urlpatterns = patterns(*p)
