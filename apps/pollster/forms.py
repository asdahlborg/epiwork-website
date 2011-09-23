from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from settings import LANGUAGES
from .models import Chart

class SurveyXmlForm(forms.Form):
    surveyxml = forms.CharField(required=True)

class SurveyTranslationAddForm(forms.Form):
    language = forms.ChoiceField(label="Language", required=True, choices=LANGUAGES)

class SurveyChartAddForm(forms.Form):
    shortname = forms.RegexField(label="Short Name", max_length=30, regex=r'^[a-zA-Z0-9_]+$', required=True)

class SurveyChartEditForm(forms.ModelForm):
    shortname = forms.RegexField(label="Short Name", max_length=30, regex=r'^[a-zA-Z0-9_]+$', required=True, error_messages={'invalid': _(u'Enter a valid value consisting of letters, numbers or underscores')})
    chartwrapper = forms.CharField(widget=forms.HiddenInput, required=False)
    class Meta:
        model = Chart
        fields = ('type', 'shortname', 'chartwrapper', 'sqlsource', 'sqlfilter', 'status')

class SurveyImportForm(forms.Form):
    data = forms.FileField(label="Survey definition", required=True)
