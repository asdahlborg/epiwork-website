from django import forms
from django.utils.translation import ugettext as _

from .fields import ( AdviseField,
                      MonthYearField,
                      PostCodeField,
                      DateOrOptionField,
                      TableOptionsSingleField,
                      TableOfSelectsField, )
from .widgets import ( AdviseWidget,
                       DatePickerWidget,
                       MonthYearWidget,
                       TableOptionsSingleWidget, )

class AddPeople(forms.Form):
    name = forms.CharField(label=_('Name'), max_length=100)

