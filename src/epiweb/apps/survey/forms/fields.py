import datetime

from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib.localflavor.nl.forms import NLZipCodeField
from django.contrib.localflavor.it.forms import ITZipCodeField

from .widgets import ( AdviseWidget, MonthYearWidget,
                       DatePickerWidget, DateOrOptionPickerWidget, )

__all__ = ['AdviseField', 'MonthYearField', 'PostCodeField', 'DateOrOptionField']

class AdviseField(forms.Field):
    widget = AdviseWidget
    required = False

    def clean(self, value):
        return True

class MonthYearField(forms.Field):
    widget = MonthYearWidget
    def clean(self, value):
        """
        Validate month and year values.

        This method is derived from Django's DateField's clean()
        """
        super(MonthYearField, self).clean(value)
        if value in (None, ''):
            return None
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        try:
            year, month = value.split('-')
            year = int(year)
            month = int(month)
            return datetime.datetime(year, month, 1).date()
        except ValueError:
            pass
        raise forms.ValidationError(self.error_messages['invalid'])

class PostCodeField(forms.RegexField):
    country_fields = {
        'nl': NLZipCodeField,
        'it': ITZipCodeField,
    }

    def __init__(self, *args, **kwargs):
        self.country = kwargs.pop('country', settings.COUNTRY)
        super(PostCodeField, self).__init__(self.country, *args, **kwargs)

    def clean(self, value):
        klass = self.country_fields.get(self.country, None)
        if klass is None:
            klass = self.country_fields['nl']

        field = klass()
        return field.clean(value)

class DateOrOptionField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        self.option = kwargs.pop('option', '')
        self.widget=DateOrOptionPickerWidget(choices=[(0, self.option)])
        self.fields=[ forms.DateField(), forms.ChoiceField()]
        super(DateOrOptionField, self).__init__(fields=self.fields,
                                                widget=self.widget,
                                                *args, **kwargs)

    def compress(self, v):
        return v
