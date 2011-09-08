import datetime, time, re
from django.core import exceptions, validators
from django.forms import CharField, ValidationError
from django.utils.translation import ugettext_lazy as _
from settings import COUNTRY

YEARMONTH_INPUT_FORMATS = (
    '%Y-%m', '%m/%Y', '%m/%y', # '2006-10', '10/2006', '10/06'
)

POSTALCODE_INPUT_FORMATS = {
    'it': r'\d{5}', # e.g. 10100
}

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

class PostalCodeField(CharField):
    default_error_messages = {
        'invalid': _('Enter a valid postal code.'),
    }

    @staticmethod
    def get_default_postal_code_format():
        return POSTALCODE_INPUT_FORMATS.get(COUNTRY);

    def __init__(self, input_format=None, *args, **kwargs):
        super(PostalCodeField, self).__init__(*args, **kwargs)
        self.input_format = input_format

    def clean(self, value):
        """
        Validate postal codes.
        """
        if value in validators.EMPTY_VALUES:
            return None
        fmt = self.input_format or PostalCodeField.get_default_postal_code_format()
        if not fmt:
            return value
        if re.match('^'+fmt+'$', value):
            return value
        raise ValidationError(self.error_messages['invalid'])
