from re import match

from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from django.conf.urls.defaults import *

from .handlers import GetUserProfile, GetReportSurvey, Report

auth = HttpBasicAuthentication(realm="EIP")
ad = { 'authentication': auth }

resources = [ 
              (GetUserProfile, ('uid',)),
              (GetReportSurvey, ('language',)),
              (Report, ('uid', 'reports',)),
            ]

with_attrs = [url(r'^%s/%s' % (handler.__name__, "/".join([r'(?P<%s>[^/]+)' % attr for attr in attrs])),
                Resource(handler=handler, **ad)
                #, {'emitter_format': 'json'}
                )
                for handler, attrs in resources]

without_attrs = [url(r'^%s' % handler.__name__,
                Resource(handler=handler, **ad)
                #, {'emitter_format': 'json'}
                )
                for handler, attr in resources]

urlpatterns = patterns("",
    *(
    with_attrs + \
    without_attrs
    )
)

