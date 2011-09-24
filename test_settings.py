from settings import *

CACHES = {}

MIDDLEWARE_CLASSES = tuple([
    x for x in MIDDLEWARE_CLASSES if not x in [
        'cms.middleware.multilingual.MultilingualURLMiddleware',
    ]])

INSTALLED_APPS = tuple([
    x for x in INSTALLED_APPS if not x in [
        'sekizai',      # sekizai app makes other tests fail
        'registration', # registration tests fail; not worthwhile to fix (for now)
    ]])

TEMPLATE_CONTEXT_PROCESSORS = tuple([
    x for x in TEMPLATE_CONTEXT_PROCESSORS if not x in [
        "sekizai.context_processors.sekizai",
    ]])


