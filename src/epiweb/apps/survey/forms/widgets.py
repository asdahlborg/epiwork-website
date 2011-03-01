import datetime
import re
import codecs

from django import forms
from django.forms.widgets import Widget, Select, RadioInput
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.utils.encoding import StrAndUnicode, force_unicode

__all__ = ['AdviseWidget', 'DatePickerWidget', 'MonthYearWidget',
           'TableOptionsSingleWidget']

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
                   forms.CheckboxSelectMultiple(choices=choices), )
        super(DateOrOptionPickerWidget, self).__init__(widget, attrs=attrs)

    def decompress(self,value):
        if value is None:
            return [None, None]
        else:
            if isinstance(value, datetime.date):
                return [str(value), None]
            else:
                return [None, value]

class RadioInputNoLabel(RadioInput):
    """
    An object used by RadioFieldRenderer that represents a single
    <input type='radio'>.
    """

    def __unicode__(self):
        return mark_safe(u'%s' % self.tag())

class TableOptionsSingleRowRenderer(StrAndUnicode):
    """
    An object used by RadioSelect to enable customization of radio widgets.
    """

    def __init__(self, name, value, attrs, choices):
        self.name, self.value, self.attrs = name, value, attrs
        self.choices = choices

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield RadioInputNoLabel(self.name, self.value,
                                    self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return RadioInputNoLabel(self.name, self.value, self.attrs.copy(),
                                 choice, idx)

    def __unicode__(self):
        return self.render()

    def render(self):
        """Outputs a <ul> for this set of radio fields."""
        return mark_safe(u''.join([u'<td>%s</td>'
                % force_unicode(w) for w in self]))
    
class TableOptionsSingleWidget(forms.MultiWidget):
    def __init__(self, options, rows, attrs=None):
        self.options = options
        self.rows = rows

        widgets = []
        for key, label in rows:
            widget = forms.RadioSelect(choices=list(options),
                                       renderer=TableOptionsSingleRowRenderer)
            widget.label = label
            widgets.append(widget)
        super(TableOptionsSingleWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value
        else:
            return [None] * len(self.rows)

    def render(self, name, value, attrs=None):
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        output.append('<table class="table-options-single">')
        output.append('<tr><th></th>')
        for key, val in self.options:
            output.append('<th>%s</th>' % val)
        output.append('</tr>')
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            output.append('<tr><td>%s</td>' % widget.label)
            output.append(widget.render(name + '_%s' % i, widget_value, final_attrs))
            output.append('</tr>')
        output.append('</table>')
        output = map(lambda x: codecs.decode(x, 'utf-8'), output)
        return mark_safe(self.format_output(output))

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

class TableOfSelectsWidget(forms.MultiWidget):

    def __init__(self, rows, columns, choices, attrs=None):
        self.rows = rows
        self.columns = columns
        self.choices = choices

        widgets = [forms.Select(choices=self.choices)
                   for r in rows
                   for c in columns]
        super(TableOfSelectsWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        return value or [None] * len(self.rows)

    def render(self, name, value, attrs=None):
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)

        output = []
        def a(s):
            output.append(s)

        a('<table border="1" class="table-of-selects">')
        a('<tr>')
        for column in ['']+self.columns:
            a('<th>%s</th>' % column)
        a('</tr>')
        for i, row in enumerate(self.rows):
            a('<tr style="text-align:right"><th>%s</th>' % row)
            for j, column in enumerate(self.columns):
                index = len(self.columns) * i + j
                widget_name = name + '_%d' % index
                try:
                    widget_value = value[index]
                except IndexError:
                    widget_value = None
                if id_:
                    final_attrs = dict(final_attrs, id='%s_%d' % (id_, index))
                widget = self.widgets[index]
                wr = widget.render(widget_name, widget_value, final_attrs)
                a('<td>%s</td>' % wr)
            a('</tr>')
        a('</table>')

        output = map(lambda x: codecs.decode(x, 'utf-8'), output)
        return mark_safe(self.format_output(output))

