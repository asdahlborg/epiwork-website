from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from cms.plugins.text.widgets.wymeditor_widget import WYMEditor

from nani.forms import TranslatableModelForm

from .models import ReminderSettings, NewsLetterTemplate, NewsLetter, get_default_for_newsitem, get_upcoming_dates

class ReminderSettingsForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(ReminderSettingsForm, self).clean()
        if cleaned_data.get('send_reminders') and not (cleaned_data.get('begin_date') and cleaned_data.get('interval')):
            raise forms.ValidationError(_("If 'send_reminders' is checked the other fields pertaining to reminders are required"))
        return cleaned_data

    class Meta:
        model = ReminderSettings

class NewsLetterTemplateForm(TranslatableModelForm):
    message = forms.CharField(widget=WYMEditor())

    class Meta:
        model = NewsLetterTemplate

class NewsLetterForm(TranslatableModelForm):
    message = forms.CharField(widget=WYMEditor())
    date = forms.ChoiceField(help_text=_("If no dates are shown here, check your site settings"))

    def __init__(self, *args, **kwargs):
        super(NewsLetterForm, self).__init__(*args, **kwargs)
        
        self.fields['date'].choices = get_upcoming_dates(datetime.now())
        for fieldname in ['sender_email', 'sender_name', 'subject', 'message']:
            self.fields[fieldname].initial = getattr(get_default_for_newsitem(self.language), fieldname) if get_default_for_newsitem(self.language) else "" 

    class Meta:
        model = NewsLetter
