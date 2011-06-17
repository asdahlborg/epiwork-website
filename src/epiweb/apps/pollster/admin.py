from django.contrib import admin

from .models import RuleType, QuestionDataType, VirtualOptionDataType

admin.site.register(RuleType)
admin.site.register(QuestionDataType)
admin.site.register(VirtualOptionDataType)

