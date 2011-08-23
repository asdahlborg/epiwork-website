import datetime, time
from django.core import exceptions, validators
from django.forms import CharField
from django.utils.translation import ugettext_lazy as _

YEARMONTH_INPUT_FORMATS = (
    '%Y-%m', '%m/%Y', '%m/%y', # '2006-10', '10/2006', '10/06'
)

class YearMonthField(CharField):
    default_error_messages = {
        'invalid': _('Enter a valid year and month.'),
    }

    def __init__(self, input_formats=None, *args, **kwargs):
        super(YearMonthField, self).__init__(*args, **kwargs)
        self.input_formats = input_formats

    def clean(self, value):
        """
        Validate month and year values.
        
        Returns a string object in YYYY-MM format.
        """
        if value in validators.EMPTY_VALUES:
            return None
        if isinstance(value, datetime.datetime):
            return format(value, '%Y-%m')
        if isinstance(value, datetime.date):
            return format(value, '%Y-%m')
        for fmt in self.input_formats or YEARMONTH_INPUT_FORMATS:
            try:
                date = datetime.date(*time.strptime(value, fmt)[:3])
                return format(date, '%Y-%m')
            except ValueError:
                continue
        raise ValidationError(self.error_messages['invalid'])
