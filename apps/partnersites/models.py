from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.conf import settings

class SiteSettings(models.Model):
    site = models.OneToOneField(Site)
    logo = models.ImageField(_("Logo"), help_text=_("Preferred height: 70px, maximum width: 756px"), upload_to='uploads', blank=True, null=True)
    light_color = models.CharField(max_length=6, default="ce2626")
    footer = models.TextField(_("Footer"), help_text=_("The footer will be displayed at the bottom of each page"), blank=True, null=True)
    contact_form_recipient = models.EmailField(blank=True, default=settings.MANAGERS[0][1])

    @property
    def dark_color(self):
        r, g, b = int(self.light_color[:2], 16), int(self.light_color[2:4], 16), int(self.light_color[4:], 16)
        return "".join("%02x" % int(c / 1.373) for c in [r, g, b])

    def __unicode__(self):
        return _(u"Site settings")

    class Meta:
        verbose_name = _("Site settings")
        verbose_name_plural = _("Site settings")

    @classmethod
    def get(cls, site):
        settings, _ = cls.objects.get_or_create(site=site)
        return settings

