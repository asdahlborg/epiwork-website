import datetime
import re

from django import forms
from django.forms.widgets import Widget, Select
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe

__all__ = ['AdviseWidget', 'DatePickerWidget', 'MonthYearWidget']

class AdviseWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        return ''

class DatePickerWidget(forms.TextInput):
    def __init__(self, attrs={}):
        forms.TextInput.__init__(self, attrs={'class': 'sDateField'})
    
class DateOrOptionPickerWidget(forms.MultiWidget):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.pop('attrs', {})
        choices = kwargs.pop('choices', [])
        widget = ( DatePickerWidget(),
                   forms.RadioSelect(choices=choices), )
        super(DateOrOptionPickerWidget, self).__init__(widget, attrs=attrs)

    def decompress(self,value):
        return value or [None, None]


RE_YEAR_MONTH = re.compile(r'(\d{4})-(\d\d?)$')

class MonthYearWidget(Widget):
    """
    A Widget that asks for month and year.

    This widget is derived from Django's SelectDateWidget.
    """
    none_value = (0, '---')
    month_field = '%s_month'
    year_field = '%s_year'

    def __init__(self, attrs=None, years=None, required=True):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        self.required = required
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year, this_year-100, -1)

    def render(self, name, value, attrs=None):
        try:
            year_val = value.year
            month_val = value.month
        except (AttributeError, ValueError):
            year_val = month_val = None
            if isinstance(value, basestring):
                match = RE_YEAR_MONTH.match(value)
                if match:
                    year_val, month_val = [int(v) for v in match.groups()]

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        month_choices = MONTHS.items()
        if not (self.required and month_val):
            month_choices.append(self.none_value)
        month_choices.sort()
        local_attrs = self.build_attrs(id=self.month_field % id_)
        s = Select(choices=month_choices)
        select_html = s.render(self.month_field % name, month_val, local_attrs)
        output.append(select_html)

        year_choices = [(i, i) for i in self.years]
        if not (self.required and year_val):
            year_choices.insert(0, self.none_value)
        local_attrs['id'] = self.year_field % id_
        s = Select(choices=year_choices)
        select_html = s.render(self.year_field % name, year_val, local_attrs)
        output.append(select_html)

        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        if y == m == "0":
            return None
        if y and m:
            return '%s-%s' % (y, m)
        return data.get(name, None)

