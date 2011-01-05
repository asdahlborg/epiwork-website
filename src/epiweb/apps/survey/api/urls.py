from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from django.conf.urls.defaults import *
from epiweb.apps.survey.api.handlers import ( GetGlobalIDbyActivationCode,
                                              GetUserProfile,
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

resources = [ [GetGlobalIDbyActivationCode, 'activation_code'],
              [GetUserProfile, 'uid'],
              [GetReportSurvey, 'language'],
              [GetImage, 'type', 'uid'],
              [Report, 'uid', 'reports'],
              [GetLanguage],
              [GetStatsHeaders, 'language'],
              [GetStatistic, 'uid', 'id', 'lang'],
              ]

def reverse_rest(l):
  "Take a list of list and reverse the 'rest' (cdr) of each list"
  def rev(l):
    l.reverse()
    return l
  def rr(l):
    r = rev(l[1:])
    r.insert(0, l[0])
    return r
  return map(rr, l)
  
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
     for s in reverse_rest(resources)]

r = [url(r'^%s' % stringify(s[0]), Resource(handler=s[0], **ad)
         #, {'emitter_format': 'json'}
         )
     for s in reverse_rest(resources)]

p = q + r
p.insert(0, '')

urlpatterns = patterns(*p)
