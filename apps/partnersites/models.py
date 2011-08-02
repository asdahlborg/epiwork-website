from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _

class SiteSettings(models.Model):
    site = models.OneToOneField(Site)
    light_color = models.CharField(max_length=6, default="ce2626")

    @property
    def dark_color(self):
        r, g, b = int(self.light_color[:2], 16), int(self.light_color[2:4], 16), int(self.light_color[4:], 16)
        return "".join("%02x" % int(c / 1.373) for c in [r, g, b])

    def __unicode__(self):
        return _(u"Site settings")

    class Meta:
        verbose_name = _("Site settings")
        verbose_name_plural = _("Site settings")

