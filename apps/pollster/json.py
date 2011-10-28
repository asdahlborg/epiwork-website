from django.utils.simplejson import *
from django.utils import simplejson
import datetime

class JSONEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return simplejson.JSONEncoder.default(self, obj)

def dumps(*args, **kwargs):
    if 'cls' not in kwargs:
        kwargs['cls'] = JSONEncoder
    return simplejson.dumps(*args, **kwargs)
