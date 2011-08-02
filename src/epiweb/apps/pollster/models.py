from django.db import models, connection
from django.contrib.auth.models import User
from django.forms import ModelForm
# TODO enable when migrating to django > 1.1
#from django.core.validators import RegexValidator
from xml.etree import ElementTree
import re, warnings, datetime
from . import dynamicmodels

SURVEY_STATUS_CHOICES = (
    ('DRAFT', 'Draft'),
    ('PUBLISHED', 'Published'),
    ('UNPUBLISHED', 'Unpublished')
)

QUESTION_TYPE_CHOICES = (
    ('builtin', 'Builtin'),
    ('text', 'Open Answer'),
    ('single-choice', 'Single Choice'),
    ('multiple-choice', 'Multiple Choice'),
    ('matrix-select', 'Matrix Select'),
    ('matrix-entry', 'Matrix Entry'),
)

class Survey(models.Model):
    parent = models.ForeignKey('self', db_index=True, blank=True, null=True)
    title = models.CharField(max_length=255, default='')
    shortname = models.SlugField(max_length=255, default='')
    version = models.SlugField(max_length=255, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, default='DRAFT', choices=SURVEY_STATUS_CHOICES)

    form = None

    _standard_result_fields =[
        ('user', models.IntegerField(null=True, blank=True)),
        ('global_id', models.CharField(max_length=36, null=True, blank=True)),
        ('channel', models.CharField(max_length=36, null=True, blank=True))
    ]

    @property
    def is_draft(self):
        return self.status == 'DRAFT'

    @property
    def is_published(self):
        return self.status == 'PUBLISHED'

    @property
    def is_unpublished(self):
        return self.status == 'UNPUBLISHED'

    @property
    def is_editable(self):
        return self.is_draft or self.is_unpublished

    @property
    def questions(self):
        for question in self.question_set.all():
            question.set_form(self.form)
            yield question

    @models.permalink
    def get_absolute_url(self):
        return ('pollster_survey_edit', [str(self.id)])

    def __unicode__(self):
        return "#%d %s" % (self.id, self.title)

    def get_table_name(self):
        if self.is_published and not self.shortname:
            raise RuntimeError('cannot generate tables for surveys with no shortname')
        if self.version:
            return 'results_'+str(self.shortname)+'_'+str(self.version)
        else:
            return 'results_'+str(self.shortname)

    def get_last_partecipation_data(self, user_id, global_id):
        model = self.as_model()
        partecipation = model.objects\
            .filter(user=user_id)\
            .filter(global_id = global_id)\
            .order_by('-timestamp')[0:1]\
            .values()[0:1]
        if partecipation:
            return partecipation[0]
        return None

    def as_model(self):
        fields = []
        fields.extend(Survey._standard_result_fields)
        for question in self.questions:
            fields += question.as_fields()
        model = dynamicmodels.create(self.get_table_name(), fields=dict(fields), app_label='pollster')
        return model

    def as_form(self):
        model = self.as_model()
        questions = list(self.questions)
        def clean(self):
            for question in questions:
                if question.is_multiple_choice and question.is_mandatory:
                    valid = any([self.cleaned_data.get(d, False) for d in question.data_names])
                    if not valid:
                        self._errors[question.data_name] = self.error_class('At least one option should be selected')
            return self.cleaned_data
        form = dynamicmodels.to_form(model, {'clean': clean})

        for question in questions:
            if question.is_mandatory and question.data_name in form.base_fields:
                form.base_fields[question.data_name].required = True
        return form

    def set_form(self, form):
        self.form = form

    def publish(self):
        if self.is_published:
            return
        self.status = 'PUBLISHED'
        model = self.as_model()
        table = model._meta.db_table
        if table in connection.introspection.table_names():
            now = datetime.datetime.now()
            backup = table+'_'+format(now, '%Y%m%d%H%M%s')
            connection.cursor().execute('ALTER TABLE '+table+' RENAME TO '+backup)
        dynamicmodels.install(model)
        self.save()

    def unpublish(self):
        if not self.is_published:
            return
        self.status = 'UNPUBLISHED'
        self.save()

class RuleType(models.Model):
    title = models.CharField(max_length=255, unique=True)
    js_class = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

class QuestionDataType(models.Model):
    title = models.CharField(max_length=255, unique=True)
    db_type = models.CharField(max_length=255)
    css_class = models.CharField(max_length=255)
    js_class = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

    def as_field_type(self, verbose_name=None, regex=None):
        import django.db.models
        field = eval(self.db_type)
        field.verbose_name = verbose_name
        # TODO enable when migrating to django > 1.1
        #if regex:
        #    field.validators.append(RegexValidator(regex=regex))
        return field

    @staticmethod
    def default_type():
        return QuestionDataType.objects.filter(title = 'Text')[0]

    @staticmethod
    def default_timestamp_type():
        return QuestionDataType.objects.filter(title = 'Timestamp')[0]

class VirtualOptionType(models.Model):
    title = models.CharField(max_length=255)
    question_data_type = models.ForeignKey(QuestionDataType)
    js_class = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

class Question(models.Model):
    survey = models.ForeignKey(Survey, db_index=True)
    starts_hidden = models.BooleanField(default=False)
    is_mandatory = models.BooleanField(default=False)
    ordinal = models.IntegerField()
    title = models.CharField(max_length=255, default='')
    description = models.TextField(blank=True, default='')
    type = models.CharField(max_length=255, choices=QUESTION_TYPE_CHOICES)
    data_type = models.ForeignKey(QuestionDataType)
    open_option_data_type = models.ForeignKey(QuestionDataType, related_name="questions_with_open_option", null=True, blank=True)
    data_name = models.CharField(max_length=255)
    visual = models.CharField(max_length=255, blank=True, default='')
    tags = models.CharField(max_length=255, blank=True, default='')
    regex = models.CharField(max_length=1023, blank=True, default='')
    error_message = models.TextField(blank=True, default='')

    form = None

    @property
    def errors(self):
        if not self.form:
            return {}
        errors = [(data_name, self.form.errors[data_name]) for data_name in self.data_names if data_name in self.form.errors]
        if self.is_multiple_choice and self.data_name in self.form.errors:
            errors.append((self.data_name, self.form.errors[self.data_name]))
        return dict(errors)

    @property
    def data_names(self):
        return [data_name for data_name, data_type in self.as_fields()]

    @property
    def options(self):
        for option in self.option_set.all():
            option.set_form(self.form)
            yield option

    @property
    def css_classes(self):
        c = ['question', 'question-'+self.type, self.data_type.css_class]
        if self.starts_hidden:
            c.append('starts-hidden')
        if self.is_mandatory:
            c.append('mandatory')
        if self.errors:
            c.append('error')
        return c

    @property
    def form_value(self):
        if not self.form:
            return ''
        return self.form.data.get(self.data_name, '')

    @property
    def is_builtin(self):
        return self.type == 'builtin'

    @property
    def is_text(self):
        return self.type == 'text'

    @property
    def is_single_choice(self):
        return self.type == 'single-choice'

    @property
    def is_multiple_choice(self):
        return self.type == 'multiple-choice'

    @property
    def is_matrix_select(self):
        return self.type == 'matrix-select'

    @property
    def is_matrix_entry(self):
        return self.type == 'matrix-entry'

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['survey', 'ordinal']

    @property
    def value(self):
        if self.is_builtin and self.data_name == 'timestamp':
            return datetime.datetime.now()
        else:
            raise NotImplementedError()

    def data_name_for_row_column(self, row, column):
        return '%s_r%d_c%d' % (self.data_name, row.ordinal, column.ordinal)

    def as_fields(self):
        fields = []
        if self.type == 'builtin':
            fields = [ (self.data_name, self.data_type.as_field_type(verbose_name=self.title)) ]
        elif self.type == 'text':
            fields = [ (self.data_name, self.data_type.as_field_type(verbose_name=self.title, regex=self.regex)) ]
        elif self.type == 'single-choice':
            open_option_data_type = self.open_option_data_type or self.data_type
            fields = [ (self.data_name, self.data_type.as_field_type(verbose_name=self.title)) ]
            for open_option in [o for o in self.option_set.all() if o.is_open]:
                fields.append( (open_option.open_option_data_name, open_option_data_type.as_field_type()) )
        elif self.type == 'multiple-choice':
            fields = []
            for option in self.option_set.all():
                title = ": ".join((self.title, option.name))
                fields.append( (option.data_name, models.BooleanField(verbose_name=title)) )
                if option.is_open:
                    fields.append( (option.open_option_data_name, option.open_option_data_type.as_field_type()) )
        elif self.type in ('matrix-select', 'matrix-entry'):
            fields = []
            for row in self.row_set.all():
                for column in self.column_set.all():
                    fields.append( (self.data_name_for_row_column(row, column), self.data_type.as_field_type()) )
        else:
            raise NotImplementedError(self.type)
        return fields

    def set_form(self, form):
        self.form = form

class QuestionRow(models.Model):
    question = models.ForeignKey(Question, related_name="row_set", db_index=True)
    ordinal = models.IntegerField()
    title = models.CharField(max_length=255, default='')

    class Meta:
        ordering = ['question', 'ordinal']

class QuestionColumn(models.Model):
    question = models.ForeignKey(Question, related_name="column_set", db_index=True)
    ordinal = models.IntegerField()
    title = models.CharField(max_length=255, default='')

    class Meta:
        ordering = ['question', 'ordinal']

class Option(models.Model):
    question = models.ForeignKey(Question, db_index=True)
    clone = models.ForeignKey('self', db_index=True, blank=True, null=True)
    row = models.ForeignKey(QuestionRow, blank=True, null=True)
    column = models.ForeignKey(QuestionColumn, blank=True, null=True)
    is_virtual = models.BooleanField(default=False)
    is_open = models.BooleanField(default=False)
    starts_hidden = models.BooleanField(default=False)
    ordinal = models.IntegerField()
    name = models.CharField(max_length=255, default='')
    text = models.TextField(default='')
    group = models.CharField(max_length=255, blank=True, default='')
    value = models.CharField(max_length=255, default='')

    virtual_type = models.ForeignKey(VirtualOptionType, blank=True, null=True)
    virtual_inf = models.CharField(max_length=255, blank=True, default='')
    virtual_sup = models.CharField(max_length=255, blank=True, default='')
    virtual_regex = models.CharField(max_length=255, blank=True, default='')

    form = None

    @property
    def data_name(self):
        if self.question.type in ('text', 'single-choice'):
            return self.question.data_name
        elif self.question.type == 'multiple-choice':
            return self.question.data_name+'_'+self.value
        elif self.question.type in ('matrix-select', 'matrix-entry'):
            return self.question.data_name_for_row_column(self.row, self.column)
        else:
            raise NotImplementedError(self.question.type)

    @property
    def open_option_data_name(self):
        return self.question.data_name+'_'+self.value+'_open'

    @property
    def open_option_data_type(self):
        return self.question.open_option_data_type or self.question.data_type

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['question', 'ordinal']

    @property
    def form_value(self):
        if not self.form:
            return ''
        return self.form.data.get(self.data_name, '')

    @property
    def open_option_data_form_value(self):
        if not self.form:
            return ''
        return self.form.data.get(self.open_option_data_name, '')

    @property
    def form_is_checked(self):
        if self.question.type in ('text', 'single-choice'):
            return self.form_value == self.value
        elif self.question.type == 'multiple-choice':
            return bool(self.form_value)
        elif self.question.type in ('matrix-select', 'matrix-entry'):
            return self.form_value == self.value
        else:
            raise NotImplementedError(self.question.type)

    def set_form(self, form):
        self.form = form

class Rule(models.Model):
    rule_type = models.ForeignKey(RuleType)
    subject_question = models.ForeignKey(Question, related_name='subject_of_rules', db_index=True)
    subject_options = models.ManyToManyField(Option, related_name='subject_of_rules', limit_choices_to = {'question': subject_question})
    object_question = models.ForeignKey(Question, related_name='object_of_rules', blank=True, null=True)
    object_options = models.ManyToManyField(Option, related_name='object_of_rules', limit_choices_to = {'question': object_question})

    def js_class(self):
        return self.rule_type.js_class

    def __unicode__(self):
        return '%s on question %s' % (self.rule_type, self.subject_question.id)

