"""In the pollster approach we no longer see Postalcodes as a separate field
These files are kept for backwards compatability"""

import datetime
import re

from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib.localflavor.it.forms import ITZipCodeField
from django.contrib.localflavor.nl.forms import NLZipCodeField
from django.contrib.localflavor.uk.forms \
     import UKPostcodeField as fullUKPostcodeField
from django.contrib.localflavor.be.forms import BEPostalCodeField
from django.contrib.localflavor.pt.forms import PTZipCodeField
from django.contrib.localflavor.se.forms import SEPostalCodeField

from .widgets import ( AdviseWidget, MonthYearWidget,
                       DatePickerWidget, DateOrOptionPickerWidget,
                       TableOptionsSingleWidget, TableOfSelectsWidget, )

__all__ = ['AdviseField', 'MonthYearField', 'PostCodeField', 'DateOrOptionField',
           'TableOptionsSingleField', 'TableOfSelectsField', ]

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

class UKPostcodeField(fullUKPostcodeField):
    """Accept and check only the outcode_pattern of the UK postcode. This is
    necessary for privacy reasons since the full post code gives too accurate a
    fix on the participant.
    """
    outcode_pattern = fullUKPostcodeField.outcode_pattern
    postcode_regex = re.compile(r'^(GIR|%s)$' % outcode_pattern)

    def clean(self, value):
        value = super(UKPostcodeField, self).clean(value)
        if value == u'':
            return value
        postcode = value.upper().strip()
        if not self.postcode_regex.search(postcode):
            raise ValidationError(self.default_error_messages['invalid'])
        return postcode

class PostCodeField(forms.RegexField):
    country_fields = {
        'be': BEPostalCodeField,
        'it': ITZipCodeField,
        'nl': NLZipCodeField,
        'pt': PTZipCodeField,
        'se': SEPostalCodeField,
        'uk': UKPostcodeField,
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
        datefield = forms.DateField(required=False,
                                    help_text="Date format: day/month/year",
                                    input_formats=['%Y-%m-%d', '%d/%m/%Y',
                                                   '%d/%m/%y', '%d-%m-%y',
                                                   '%d-%m-%Y', '%b %d %Y',
                                                   '%b %d, %Y', '%d %b %Y',
                                                   '%d %b, %Y', '%B %d %Y',
                                                   '%B %d, %Y', '%d %B %Y',
                                                   '%d %B, %Y'])
        self.datefield = datefield
        self.fields=[datefield,
                     forms.ChoiceField(required=False)]
        super(DateOrOptionField, self).__init__(fields=self.fields,
                                                widget=self.widget,
                                                *args, **kwargs)

    def compress(self, v):
        return v
    def clean(self, value):
        date, choice = value
        if len(choice) > 0:    # option was chosen
            return choice[0]
        else:                  # use the date
            date = self.datefield.clean(date)
            if date is None:
                if self.required:
                    raise forms.ValidationError(self.error_messages['required'])
                return None
            return date

class TableOfSelectsField(forms.MultiValueField):

    def __init__(self, rows, columns, choices, *args, **kwargs):
        fields = [forms.ChoiceField(label=row, choices=choices, required=False)
                  for row in rows
                  for column in columns]
        kwargs['widget'] = TableOfSelectsWidget(rows, columns, choices)
        super(TableOfSelectsField, self).__init__(fields, *args, **kwargs)

    def compress(self, v):
        return v

    def clean(self, value):
        return value

class TableOptionsSingleField(forms.MultiValueField):
    def __init__(self, options, rows, required_rows=None, *args, **kwargs):
        self.options = options
        self.rows = rows
        self.required_rows = required_rows
        if not 'widget' in kwargs:
            widget = TableOptionsSingleWidget(options=self.options,
                                              rows=self.rows)
            kwargs['widget'] = widget
        if not 'fields' in kwargs:
            fields = []
            for key, label in self.rows:
                field = forms.ChoiceField(label=label,
                                          required=False,
                                          choices=list(self.options))
                fields.append(field)
            kwargs['fields'] = fields
        super(TableOptionsSingleField, self).__init__(**kwargs)

    def compress(self, value):
        return value
    def clean(self, value):
        return value
    def clean_all(self, field, values):
        required = self.required_rows
        if required is None:
            required = range(0, len(self.rows))
        elif callable(required):
            required = required(values)
        filled = []
        if values[field] is not None:
            for index, value in enumerate(values[field]):
                if value is not None:
                    filled.append(index)
        for index in required:
            if not index in filled:
                raise forms.ValidationError('Incomplete answer')
        return values[field]

