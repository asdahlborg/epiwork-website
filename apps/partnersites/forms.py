from django import forms
from django.utils.translation import ugettext_lazy as _

from cms.plugins.text.widgets.wymeditor_widget import WYMEditor

from .models import SiteSettings

class SiteSettingsForm(forms.ModelForm):
    light_color = forms.RegexField(label=_("Light color"), help_text=_("Hexidecimal value w/o preceding '#'; The dark color is calculated from this."), regex='[0-9a-fA-F]{6}', error_messages={'invalid': _('Use a hexidecimal value (length: 6) without the preceding #')})
    footer = forms.CharField(widget=WYMEditor(), required=False)

    def save(self, commit=True):
        result = super(SiteSettingsForm, self).save(commit=False)
        result.light_color = result.light_color.lower()
        if commit:
            result.save()
        return result

    class Meta:
        model = SiteSettings

