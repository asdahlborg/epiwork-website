from django import forms
from django.utils.translation import ugettext as _

from .fields import AdviseField, MonthYearField, PostCodeField
from .widgets import AdviseWidget, DatePickerWidget, MonthYearWidget

class AddPeople(forms.Form):
    name = forms.CharField(label=_('Name'), max_length=100)

