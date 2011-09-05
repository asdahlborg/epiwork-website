from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.conf import settings

from loginurl.views import cleanup, login

urlpatterns = patterns('apps.reminder.views',
    (r'^unsubscribe/$', 'unsubscribe'), 
)

