from __future__ import absolute_import

from ... import fields
from django.db.models.fields import CharField
from django.core import exceptions, validators
from django.utils.translation import ugettext_lazy as _

class YearMonthField(CharField):
    description = _("Year and month (in YYYY-MM format)")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        super(YearMonthField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    def formfield(self, **kwargs):
        defaults = {'form_class': fields.YearMonthField}
        defaults.update(kwargs)
        return super(YearMonthField, self).formfield(**defaults)

class PostalCodeField(CharField):
    description = _("Postal code")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 30
        super(PostalCodeField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    def formfield(self, **kwargs):
        defaults = {'form_class': fields.PostalCodeField}
        defaults.update(kwargs)
        return super(PostalCodeField, self).formfield(**defaults)
