from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

class SanderApphook(CMSApp):
    name = "Sander's result page"
    urls = ["apps.sander.urls"]

apphook_pool.register(SanderApphook)

