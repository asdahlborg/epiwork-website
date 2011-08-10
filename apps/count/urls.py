from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
    url(r'^counter', views.counter, name='counter'),
    url(r'^list', views.list, name='list'),
)
