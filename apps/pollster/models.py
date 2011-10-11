from django.db import models, connection, transaction, IntegrityError, DatabaseError
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.core.validators import RegexValidator
from cms.models import CMSPlugin
from xml.etree import ElementTree
from math import pi,cos,sin,log,exp,atan
from . import dynamicmodels, json
import os, re, shutil, warnings, datetime
import settings

DEG_TO_RAD = pi/180
RAD_TO_DEG = 180/pi

try:
    import mapnik2 as mapnik
except:
    import mapnik

SURVEY_STATUS_CHOICES = (
    ('DRAFT', 'Draft'),
    ('PUBLISHED', 'Published'),
    ('UNPUBLISHED', 'Unpublished')
)

SURVEY_TRANSLATION_STATUS_CHOICES = (
    ('DRAFT', 'Draft'),
    ('PUBLISHED', 'Published')
)

CHART_STATUS_CHOICES = (
    ('DRAFT', 'Draft'),
    ('PUBLISHED', 'Published'),
)

QUESTION_TYPE_CHOICES = (
    ('builtin', 'Builtin'),
    ('text', 'Open Answer'),
    ('single-choice', 'Single Choice'),
    ('multiple-choice', 'Multiple Choice'),
    ('matrix-select', 'Matrix Select'),
    ('matrix-entry', 'Matrix Entry'),
)

CHART_SQLFILTER_CHOICES = (
    ('NONE', 'None'),
    ('USER', 'Current User'),
    ('PERSON', 'Current Person'),
)

IDENTIFIER_REGEX = r'^[a-zA-Z][a-zA-Z0-9_]*$'
IDENTIFIER_OPTION_REGEX = r'^[a-zA-Z0-9_]*$'

SURVEY_EXTRA_SQL = {
    'postgresql': {
        'weekly': [
            """DROP VIEW IF EXISTS pollster_health_status""",
            """CREATE VIEW pollster_health_status AS
               SELECT id as pollster_results_weekly_id,
                      case true
                          when "QN1_0"
                              then 'NO-SYMPTOMS'
                          when "QN5" = 0
                           and ("QN1_1" or "QN1_11" or "QN1_8" or "QN1_9")
                           and ("QN1_5" or "QN1_6" or "QN1_7")
                              then 'ILI'
                          when "QN5" = 1
                           and ("QN1_4" or "QN1_5" or "QN1_6" or "QN1_7")
                              then 'COMMON-COLD'
                          when "QN1_15" or "QN1_16" or "QN1_17" and "QN1_18"
                              then 'GASTROINTESTINAL'
                          else 'NON-INFLUENZA'
                      end as status
                 FROM pollster_results_weekly"""
        ]
    },
    'sqlite': {
        'weekly': [
            """DROP VIEW IF EXISTS pollster_health_status""",
            """CREATE VIEW pollster_health_status AS
               SELECT id as pollster_results_weekly_id,
                      case 1
                          when QN1_0
                              then 'NO-SYMPTOMS'
                          when QN5 == 0
                           and (QN1_1 or QN1_11 or QN1_8 or QN1_9)
                           and (QN1_5 or QN1_6 or QN1_7)
                              then 'ILI'
                          when QN5 == 1
                           and (QN1_4 or QN1_5 or QN1_6 or QN1_7)
                              then 'COMMON-COLD'
                          when QN1_15 or QN1_16 or QN1_17 and QN1_18
                              then 'GASTROINTESTINAL'
                          else 'NON-INFLUENZA'
                      end as status
                 FROM pollster_results_weekly"""
        ]
    }
}

def _get_or_default(queryset, default=None):
    r = queryset[0:1]
    if r:
        return r[0]
    return default


class Survey(models.Model):
    parent = models.ForeignKey('self', db_index=True, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, default='')
    shortname = models.SlugField(max_length=255, default='')
    version = models.SlugField(max_length=255, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, default='DRAFT', choices=SURVEY_STATUS_CHOICES)

    form = None
    translation_survey = None

    _standard_result_fields =[
        ('user', models.IntegerField(null=True, blank=True)),
        ('global_id', models.CharField(max_length=36, null=True, blank=True)),
        ('channel', models.CharField(max_length=36, null=True, blank=True))
    ]

    @staticmethod
    def get_by_shortname(shortname):
        return Survey.objects.all().get(shortname=shortname, status="PUBLISHED")

    @property
    def translated_title(self):
        if self.translation and self.translation.title:
            return self.translation.title
        return self.title

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
            question.set_translation_survey(self.translation_survey)
            yield question

    @property
    def translation(self):
        return self.translation_survey

    @models.permalink
    def get_absolute_url(self):
        return ('pollster_survey_edit', [str(self.id)])

    def __unicode__(self):
        return "Survey #%d %s" % (self.id, self.title)

    def get_table_name(self):
        if self.is_published and not self.shortname:
            raise RuntimeError('cannot generate tables for surveys with no shortname')
        if self.version:
            return 'results_'+str(self.shortname)+'_'+str(self.version)
        else:
            return 'results_'+str(self.shortname)

    def get_last_participation_data(self, user_id, global_id):
        model = self.as_model()
        participation = model.objects\
            .filter(user=user_id)\
            .filter(global_id = global_id)\
            .order_by('-timestamp')\
            .values()
        return _get_or_default(participation)

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

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey

    def check(self):
        errors = []
        if not self.shortname:
            errors.append('Missing survey shortname')
        elif not re.match(IDENTIFIER_REGEX, self.shortname):
            errors.append('Invalid survey shortname "%s"' % (self.shortname,))
        for question in self.questions:
            errors.extend(question.check())
        return errors

    def publish(self):
        if self.is_published:
            return None
        errors = self.check()
        if errors:
            return errors
        self.status = 'PUBLISHED'
        model = self.as_model()
        table = model._meta.db_table
        if table in connection.introspection.table_names():
            now = datetime.datetime.now()
            backup = table+'_'+format(now, '%Y%m%d%H%M%s')
            connection.cursor().execute('ALTER TABLE '+table+' RENAME TO '+backup)
        dynamicmodels.install(model)
        db = _get_db_type(connection)
        for extra_sql in SURVEY_EXTRA_SQL[db].get(self.shortname, []):
            connection.cursor().execute(extra_sql)
        self.save()
        return None

    def unpublish(self):
        if not self.is_published:
            return
        self.status = 'UNPUBLISHED'
        self.save()

class RuleType(models.Model):
    title = models.CharField(max_length=255, blank=True, default='')
    js_class = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return "RuleType #%d %s" % (self.id, self.title)

class QuestionDataType(models.Model):
    title = models.CharField(max_length=255, blank=True, default='')
    db_type = models.CharField(max_length=255)
    css_class = models.CharField(max_length=255)
    js_class = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return "QuestionDataType #%d %s" % (self.id, self.title)

    def as_field_type(self, verbose_name=None, regex=None):
        import django.db.models
        import db.models
        field = eval(self.db_type)
        field.verbose_name = verbose_name
        if regex:
            field.validators.append(RegexValidator(regex=regex))
        return field

    @staticmethod
    def default_type():
        return QuestionDataType.objects.filter(title = 'Text')[0]

    @staticmethod
    def default_timestamp_type():
        return QuestionDataType.objects.filter(title = 'Timestamp')[0]

class VirtualOptionType(models.Model):
    title = models.CharField(max_length=255, blank=True, default='')
    question_data_type = models.ForeignKey(QuestionDataType)
    js_class = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return "VirtualOptionType #%d %s for %s" % (self.id, self.title, self.question_data_type.title)

class Question(models.Model):
    survey = models.ForeignKey(Survey, db_index=True)
    starts_hidden = models.BooleanField(default=False)
    is_mandatory = models.BooleanField(default=False)
    ordinal = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, default='')
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
    translation_survey = None
    translation_question = None

    @property
    def translated_title(self):
        if self.translation and self.translation.title:
            return self.translation.title
        return self.title

    @property
    def translated_description(self):
        if self.translation and self.translation.description:
            return self.translation.description
        return self.description

    @property
    def translated_error_message(self):
        if self.translation and self.translation.error_message:
            return self.translation.error_message
        return self.error_message


    @property
    def errors(self):
        if not self.form:
            return {}
        errors = [(data_name, self.form.errors[data_name]) for data_name in self.data_names if data_name in self.form.errors]
        if self.is_multiple_choice and self.data_name in self.form.errors:
            errors.append((self.data_name, self.form.errors[self.data_name]))
        return dict(errors)

    @property
    def rows(self):
        for row in self.row_set.all():
            row.set_translation_survey(self.translation_survey)
            yield row

    @property
    def columns(self):
        for column in self.column_set.all():
            column.set_translation_survey(self.translation_survey)
            yield column

    @property
    def rows_columns(self):
        for row in self.rows:
            yield (row, self._columns_for_row(row))

    def _columns_for_row(self, row):
        for column in self.columns:
            column.set_row(row)
            yield column

    @property
    def data_names(self):
        return [data_name for data_name, data_type in self.as_fields()]

    @property
    def options(self):
        for option in self.option_set.all():
            option.set_form(self.form)
            option.set_translation_survey(self.translation_survey)
            yield option

    @property
    def translation(self):
        return self.translation_question

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

    @property
    def is_visual_dropdown(self):
        return self.visual == 'dropdown'

    def __unicode__(self):
        return "Question #%d %s" % (self.id, self.title)

    class Meta:
        ordering = ['survey', 'ordinal']

    def data_name_for_row_column(self, row, column):
        return '%s_multi_row%d_col%d' % (self.data_name, row.ordinal, column.ordinal)

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
                title = ": ".join((self.title, option.data_name))
                fields.append( (option.data_name, models.BooleanField(verbose_name=title)) )
                if option.is_open:
                    fields.append( (option.open_option_data_name, option.open_option_data_type.as_field_type()) )
        elif self.type in ('matrix-select', 'matrix-entry'):
            fields = []
            for row, columns in self.rows_columns:
                for column in columns:
                    fields.append( (column.data_name, self.data_type.as_field_type()) )
        else:
            raise NotImplementedError(self.type)
        return fields

    def set_form(self, form):
        self.form = form

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            r = translation_survey.translationquestion_set.all().filter(question=self)
            default = TranslationQuestion(translation = translation_survey, question=self)
            self.translation_question = _get_or_default(r, default)

    def check(self):
        errors = []
        if not self.data_name:
            errors.append('Missing data name for question "%s"' % (self.title, ))
        elif not re.match(IDENTIFIER_REGEX, self.data_name):
            errors.append('Invalid data name "%s" for question "%s"' % (self.data_name, self.title))
        values = {}
        for option in self.options:
            errors.extend(option.check())
            values[option.value] = values.get(option.value, 0) + 1
        if self.type == 'multiple-choice':
            dups = [val for val, count in values.items() if count > 1]
            for dup in dups:
                errors.append('Duplicated value %s in question %s' % (dup, self.title))
        return errors


class QuestionRow(models.Model):
    question = models.ForeignKey(Question, related_name="row_set", db_index=True)
    ordinal = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, default='')

    translation_survey = None
    translation_row = None

    class Meta:
        ordering = ['question', 'ordinal']

    def __unicode__(self):
        return "QuestionRow #%d %s" % (self.id, self.title)

    @property
    def translated_title(self):
        if self.translation and self.translation.title:
            return self.translation.title
        return self.title

    @property
    def translation(self):
        return self.translation_row

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            r = translation_survey.translationquestionrow_set.all().filter(row=self)
            default = TranslationQuestionRow(translation = translation_survey, row=self)
            self.translation_row = _get_or_default(r, default)

class QuestionColumn(models.Model):
    question = models.ForeignKey(Question, related_name="column_set", db_index=True)
    ordinal = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, default='')

    translation_survey = None
    translation_column = None
    row = None

    class Meta:
        ordering = ['question', 'ordinal']

    def __unicode__(self):
        return "QuestionColumn #%d %s" % (self.id, self.title)

    @property
    def translated_title(self):
        if self.translation and self.translation.title:
            return self.translation.title
        return self.title

    @property
    def translation(self):
        return self.translation_column

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            r = translation_survey.translationquestioncolumn_set.all().filter(column=self)
            default = TranslationQuestionColumn(translation = translation_survey, column=self)
            self.translation_column = _get_or_default(r, default)

    def set_row(self, row):
        self.row = row

    @property
    def options(self):
        for option in self.question.options:
            if option.row and option.row != self.row:
                continue
            if option.column and option.column != self:
                continue
            option.set_row_column(self.row, self)
            yield option

    @property
    def data_name(self):
        if not self.row:
            raise NotImplementedError('use Question.rows_columns() to get the right data_name here')
        return self.question.data_name_for_row_column(self.row, self)

class Option(models.Model):
    question = models.ForeignKey(Question, db_index=True)
    clone = models.ForeignKey('self', db_index=True, blank=True, null=True)
    row = models.ForeignKey(QuestionRow, blank=True, null=True)
    column = models.ForeignKey(QuestionColumn, blank=True, null=True)
    is_virtual = models.BooleanField(default=False)
    is_open = models.BooleanField(default=False)
    starts_hidden = models.BooleanField(default=False)
    ordinal = models.IntegerField()
    text = models.CharField(max_length=4095, blank=True, default='')
    group = models.CharField(max_length=255, blank=True, default='')
    value = models.CharField(max_length=255, default='')
    description = models.TextField(blank=True, default='')

    virtual_type = models.ForeignKey(VirtualOptionType, blank=True, null=True)
    virtual_inf = models.CharField(max_length=255, blank=True, default='')
    virtual_sup = models.CharField(max_length=255, blank=True, default='')
    virtual_regex = models.CharField(max_length=255, blank=True, default='')

    form = None
    translation_survey = None
    translation_option = None
    current_row_column = (None, None)

    @property
    def translated_text(self):
        if self.translation and self.translation.text:
            return self.translation.text
        return self.text

    @property
    def translated_description(self):
        if self.translation and self.translation.description:
            return self.translation.description
        return self.description

    @property
    def data_name(self):
        if self.question.type in ('text', 'single-choice'):
            return self.question.data_name
        elif self.question.type == 'multiple-choice':
            return self.question.data_name+'_'+self.value
        elif self.question.type in ('matrix-select', 'matrix-entry'):
            row = self.row or self.current_row_column[0]
            column = self.column or self.current_row_column[1]
            return self.question.data_name_for_row_column(row, column)
        else:
            raise NotImplementedError(self.question.type)

    @property
    def translation(self):
        return self.translation_option

    @property
    def open_option_data_name(self):
        return self.question.data_name+'_'+self.value+'_open'

    @property
    def open_option_data_type(self):
        return self.question.open_option_data_type or self.question.data_type

    def __unicode__(self):
        return 'Option #%d %s' % (self.id, self.value)

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

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            r = translation_survey.translationoption_set.all().filter(option=self)
            default = TranslationOption(translation = translation_survey, option=self)
            self.translation_option = _get_or_default(r, default)

    def set_row_column(self, row, column):
        self.current_row_column = (row, column)

    def check(self):
        errors = []
        if self.is_virtual:
            if not self.virtual_inf and not self.virtual_sup and not self.virtual_regex:
                errors.append('Missing parameters for derived value in question "%s"' % (self.question.title, ))
        else:
            if not self.text:
                errors.append('Empty text for option in question "%s"' % (self.question.title, ))
            if not self.value:
                errors.append('Missing value for option "%s" in question "%s"' % (self.text, self.question.title))
            elif self.question.type == 'multiple-choice' and not re.match(IDENTIFIER_OPTION_REGEX, self.value):
                errors.append('Invalid value "%s" for option "%s" in question "%s"' % (self.value, self.text, self.question.title))
        return errors

class Rule(models.Model):
    rule_type = models.ForeignKey(RuleType)
    is_sufficient = models.BooleanField(default=True)
    subject_question = models.ForeignKey(Question, related_name='subject_of_rules', db_index=True)
    subject_options = models.ManyToManyField(Option, related_name='subject_of_rules', limit_choices_to = {'question': subject_question})
    object_question = models.ForeignKey(Question, related_name='object_of_rules', blank=True, null=True)
    object_options = models.ManyToManyField(Option, related_name='object_of_rules', limit_choices_to = {'question': object_question})

    def js_class(self):
        return self.rule_type.js_class

    def __unicode__(self):
        return 'Rule #%d' % (self.id)

# I18n models

class TranslationSurvey(models.Model):
    survey = models.ForeignKey(Survey, db_index=True)
    language = models.CharField(max_length=3, db_index=True)
    title = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=255, default='DRAFT', choices=SURVEY_TRANSLATION_STATUS_CHOICES)

    class Meta:
        verbose_name = 'Translation'
        ordering = ['survey', 'language']
        unique_together = ('survey', 'language')

    @models.permalink
    def get_absolute_url(self):
        return ('pollster_survey_translation_edit', [str(self.survey.id), self.language])

    def __unicode__(self):
        return "TranslationSurvey(%s) for %s" % (self.language, self.survey)

    def as_form(self, data=None):
        class TranslationSurveyForm(ModelForm):
            class Meta:
                model = TranslationSurvey
                fields = ['title', 'status']
        return TranslationSurveyForm(data, instance=self, prefix="survey")

class TranslationQuestion(models.Model):
    translation = models.ForeignKey(TranslationSurvey, db_index=True)
    question = models.ForeignKey(Question, db_index=True)
    title = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField(blank=True, default='')
    error_message = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['translation', 'question']
        unique_together = ('translation', 'question')

    def __unicode__(self):
        return "TranslationQuestion(%s) for %s" % (self.translation.language, self.question)

    def as_form(self, data=None):
        class TranslationQuestionForm(ModelForm):
            class Meta:
                model = TranslationQuestion
                fields = ['title', 'description', 'error_message']
        return TranslationQuestionForm(data, instance=self, prefix="question_%s"%(self.id,))

class TranslationQuestionRow(models.Model):
    translation = models.ForeignKey(TranslationSurvey, db_index=True)
    row = models.ForeignKey(QuestionRow, db_index=True)
    title = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['translation', 'row']
        unique_together = ('translation', 'row')

    def __unicode__(self):
        return "TranslationQuestionRow(%s) for %s" % (self.translation.language, self.row)

    def as_form(self, data=None):
        class TranslationRowForm(ModelForm):
            class Meta:
                model = TranslationQuestionRow
                fields = ['title']
        return TranslationRowForm(data, instance=self, prefix="row_%s"%(self.id,))

class TranslationQuestionColumn(models.Model):
    translation = models.ForeignKey(TranslationSurvey, db_index=True)
    column = models.ForeignKey(QuestionColumn, db_index=True)
    title = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['translation', 'column']
        unique_together = ('translation', 'column')

    def __unicode__(self):
        return "TranslationQuestionColumn(%s) for %s" % (self.translation.language, self.column)

    def as_form(self, data=None):
        class TranslationColumnForm(ModelForm):
            class Meta:
                model = TranslationQuestionColumn
                fields = ['title']
        return TranslationColumnForm(data, instance=self, prefix="column_%s"%(self.id,))

class TranslationOption(models.Model):
    translation = models.ForeignKey(TranslationSurvey, db_index=True)
    option = models.ForeignKey(Option, db_index=True)
    text = models.CharField(max_length=4095, blank=True, default='')
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['translation', 'option']
        unique_together = ('translation', 'option')

    def __unicode__(self):
        return "TranslationOption(%s) for %s" % (self.translation.language, self.option)

    def as_form(self, data=None):
        class TranslationOptionForm(ModelForm):
            class Meta:
                model = TranslationOption
                fields = ['text', 'description']
        return TranslationOptionForm(data, instance=self, prefix="option_%s"%(self.id,))

class ChartType(models.Model):
    shortname = models.SlugField(max_length=255, unique=True)
    description = models.CharField(max_length=255)

    def __unicode__(self):
        return self.description or self.shortname

class Chart(models.Model):
    survey = models.ForeignKey(Survey, db_index=True)
    type = models.ForeignKey(ChartType, db_index=True)
    shortname = models.SlugField(max_length=255)
    chartwrapper = models.TextField(blank=True, default='')
    sqlsource = models.TextField(blank=True, default='', verbose_name="SQL Source Query")
    sqlfilter = models.CharField(max_length=255, default='NONE', choices=CHART_SQLFILTER_CHOICES, verbose_name="Results Filter")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, default='DRAFT', choices=CHART_STATUS_CHOICES)

    class Meta:
        ordering = ['survey', 'shortname']
        unique_together = ('survey', 'shortname')

    def __unicode__(self):
        return "Chart %s for %s" % (self.shortname, self.survey)

    @models.permalink
    def get_absolute_url(self):
        return ('pollster_survey_chart_edit', [str(self.survey.id), self.shortname])

    @property
    def is_draft(self):
        return self.status == 'DRAFT'

    @property
    def is_published(self):
        return self.status == 'PUBLISHED'

    @property
    def has_data(self):
        if not self.sqlsource:
            return False
        else:
            return True

    def to_json(self, user_id, global_id):
        data = {}
        if self.type.shortname == "google-charts":
            data[ "chartType"] = "Table"
            if self.chartwrapper:
                data = json.loads(self.chartwrapper)
            descriptions, cells = self.load_data(user_id, global_id)
            cols = [{"id": desc[0], "label": desc[0], "type": "number"} for desc in descriptions]
            rows = [{"c": [{"v": v} for v in c]} for c in cells]
            data["dataTable"] = { "cols": cols, "rows": rows }

        else:
            if self.chartwrapper:
                data["bounds"] = json.loads(self.chartwrapper)
            # TODO: To center the map on the centroid of current user's zip we need
            # to access the "intake" survey, question "Q3". Those two values should
            # probably go into settings.py, or something like that.
            try:
                intake = Survey.objects.get(shortname="intake", status='PUBLISHED')
                lpd = intake.get_last_participation_data(user_id, global_id)
                if lpd:
                    data["center"] = self.load_zip_coords(str(lpd["QN3"]))
            except:
                pass

        return json.dumps(data)

    def get_map_click(self, lat, lng):
        result = {}
        skip_cols = ("ogc_fid", "color", "geometry")
        description, data = self.load_info(lat, lng)
        if data and len(data) > 0:
            for i in range(len(data[0])):
                if description[i][0] not in skip_cols:
                    result[description[i][0]] = str(data[0][i])
        return json.dumps(result)

    def get_map_tile(self, user_id, global_id, z, x, y):
        filename = self.get_map_tile_filename(z, x, y)
        if not os.path.exists(filename):
            self.generate_map_tile(self.generate_mapnik_map(user_id, global_id), filename, z, x, y)
        return open(filename).read()

    def generate_map_tile(self, m, filename, z, x, y):
        # Code taken from OSM generate_tiles.py
        proj = GoogleProjection()
        mprj = mapnik.Projection(m.srs)

        p0 = (x * 256, (y + 1) * 256)
        p1 = ((x + 1) * 256, y * 256)
        l0 = proj.fromPixelToLL(p0, z);
        l1 = proj.fromPixelToLL(p1, z);
        c0 = mprj.forward(mapnik.Coord(l0[0], l0[1]))
        c1 = mprj.forward(mapnik.Coord(l1[0], l1[1]))

        if hasattr(mapnik,'mapnik_version') and mapnik.mapnik_version() >= 800:
            bbox = mapnik.Box2d(c0.x, c0.y, c1.x, c1.y)
        else:
            bbox = mapnik.Envelope(c0.x, c0.y, c1.x, c1.y)

        m.resize(256, 256)
        m.zoom_to_box(bbox)

        im = mapnik.Image(256, 256)
        mapnik.render(m, im)
        im.save(str(filename), "png256")

    def generate_mapnik_map(self, user_id, global_id):
        m = mapnik.Map(256, 256)

        style = self.generate_mapnik_style(user_id, global_id)

        m.background = mapnik.Color("transparent")
        m.append_style("ZIP_CODES STYLE", style)
        m.srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over"

        layer = mapnik.Layer('ZIP_CODES')
        layer.datasource = self.create_mapnik_datasource(user_id, global_id)
        layer.styles.append("ZIP_CODES STYLE")
        m.layers.append(layer)

        return m

    def generate_mapnik_style(self, user_id, global_id):
        style = mapnik.Style()
        for color in self.load_colors(user_id, global_id):
            c = mapnik.Color(str(color))
            line = mapnik.LineSymbolizer(c, 1.5)
            line.stroke.opacity = 0.7
            poly = mapnik.PolygonSymbolizer(c)
            poly.fill_opacity = 0.5
            rule = mapnik.Rule()
            rule.filter = mapnik.Filter(str("[color] = '%s'" % (color,)))
            rule.symbols.extend([poly,line])
            style.rules.append(rule)
        return style

    def create_mapnik_datasource(self, user_id, global_id):
        # First create the SQL query that is a join between pollster_zip_codes and
        # the chart query as created by the user; then create an appropriate datasource.

        if global_id and re.findall('[^0-9A-Za-z-]', global_id):
            raise Exception("invalid global_id "+global_id)

        table = """SELECT * FROM %s""" % (self.get_view_name(),)
        if self.sqlfilter == 'USER' :
            table += """ WHERE "user" = %d""" % (user_id,)
        elif self.sqlfilter == 'PERSON':
            table += """ WHERE "user" = %d AND global_id = '%s'""" % (user_id, global_id)
        table = "(" + table + ") AS ZIP_CODES"

        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
            name = settings.DATABASES["default"]["NAME"]
            return mapnik.SQLite(file=filename, wkb_format="spatialite",
                geometry_field="geometry", estimate_extent=False, table=table)

        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
            name = settings.DATABASES["default"]["NAME"]
            host = settings.DATABASES["default"]["HOST"]
            port = settings.DATABASES["default"]["PORT"]
            username = settings.DATABASES["default"]["USER"]
            password = settings.DATABASES["default"]["PASSWORD"]
            return mapnik.PostGIS(host=host, port=port, user=username, password=password, dbname=name,
                geometry_field="geometry", estimate_extent=False, table=table)

    def get_map_tile_base(self):
        return "_pollster_tile_cache/survey_%s/%s" % (self.survey.id, self.shortname)

    def get_map_tile_filename(self, z, x, y):
        filename = "%s/%s/%s_%s.png" % (self.get_map_tile_base(), z, x, y)
        pathname = os.path.dirname(filename)
        if not os.path.exists(pathname):
            os.makedirs(pathname)
        return filename

    def clear_map_tile_cache(self):
        try:
            shutil.rmtree(self.get_map_tile_base())
        except:
            pass

    def get_table_name(self):
        return 'pollster_charts_'+str(self.survey.shortname)+'_'+str(self.shortname)

    def get_view_name(self):
        return self.get_table_name() + "_view"

    def update_table(self):
        table_query = self.sqlsource
        if table_query:
            table = self.get_table_name()
            view = self.get_view_name()
            view_query = """SELECT A.*, B.id AS OGC_FID, B.geometry
                              FROM pollster_zip_codes B, (SELECT * FROM %s) A
                             WHERE A.zip_code_key = B.zip_code_key""" % (table,)
            cursor = connection.cursor()
            try:
                cursor.execute("DROP VIEW IF EXISTS %s" % (view,))
                cursor.execute("DROP TABLE IF EXISTS %s" % (table,))
                cursor.execute("CREATE TABLE %s AS %s" % (table, table_query))
                if self.type.shortname != 'google-charts':
                    cursor.execute("CREATE VIEW %s AS %s" % (view, view_query))
                self.clear_map_tile_cache()
                return True
            except IntegrityError:
                return False
            except DatabaseError:
                return False
        return False

    def update_data(self):
        table_query = self.sqlsource
        if table_query:
            table = self.get_table_name()
            cursor = connection.cursor()
            try:
                cursor.execute("DELETE FROM %s" % (table,))
                cursor.execute("INSERT INTO %s %s" % (table, table_query))
                self.clear_map_tile_cache()
                return True
            except IntegrityError:
                return False
            except DatabaseError:
                return False
        return False

    def load_data(self, user_id, global_id):
        table = self.get_table_name()
        query = "SELECT * FROM %s" % (table,)
        if self.sqlfilter == 'USER' :
            query += """ WHERE "user" = %(user_id)s"""
        elif self.sqlfilter == 'PERSON':
            query += """ WHERE "user" = %(user_id)s AND global_id = %(global_id)s"""
        params = { 'user_id': user_id, 'global_id': global_id }
        query = _convert_query_paramstyle(connection, query, params)
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            return (cursor.description, cursor.fetchall())
        except DatabaseError, e:
            return ((('Error',),), ((str(e),),))

    def load_colors(self, user_id, global_id):
        table = self.get_table_name()
        query = """SELECT DISTINCT color FROM %s""" % (table,)
        if self.sqlfilter == 'USER' :
            query += """ WHERE "user" = %(user_id)s"""
        elif self.sqlfilter == 'PERSON':
            query += """ WHERE "user" = %(user_id)s AND global_id = %(global_id)s"""
        params = { 'user_id': user_id, 'global_id': global_id }
        query = _convert_query_paramstyle(connection, query, params)
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            return [x[0] for x in cursor.fetchall()]
        except DatabaseError, e:
            return (None, [])

    def load_info(self, lat, lng):
        view = self.get_view_name()
        query = "SELECT * FROM %s WHERE ST_Contains(geometry, 'SRID=4326;POINT(%%s %%s)')" % (view,)
        try:
            cursor = connection.cursor()
            cursor.execute(query, (lng, lat))
            return (cursor.description, cursor.fetchall())
        except DatabaseError, e:
            return (None, [])

    def load_zip_coords(self, zip_code_key):
        query = """SELECT ST_Y(ST_Centroid(geometry)) AS lat, ST_X(ST_Centroid(geometry)) AS lng
                     FROM pollster_zip_codes WHERE zip_code_key = %s"""
        try:
            cursor = connection.cursor()
            cursor.execute(query, (zip_code_key,))
            data = cursor.fetchall()
            if len(data) > 0:
                return {"lat": data[0][0], "lng": data[0][1]}
            else:
                return {}
        except DatabaseError, e:
            return {}

class GoogleProjection:
    def __init__(self,levels=18):
        self.Bc = []
        self.Cc = []
        self.zc = []
        self.Ac = []
        c = 256
        for d in range(0,levels):
            e = c/2;
            self.Bc.append(c/360.0)
            self.Cc.append(c/(2 * pi))
            self.zc.append((e,e))
            self.Ac.append(c)
            c *= 2
                
    def fromLLtoPixel(self,ll,zoom):
         d = self.zc[zoom]
         e = round(d[0] + ll[0] * self.Bc[zoom])
         f = min(max(sin(DEG_TO_RAD * ll[1]),-0.9999),0.9999)
         g = round(d[1] + 0.5*log((1+f)/(1-f))*-self.Cc[zoom])
         return (e,g)
     
    def fromPixelToLL(self,px,zoom):
         e = self.zc[zoom]
         f = (px[0] - e[0])/self.Bc[zoom]
         g = (px[1] - e[1])/-self.Cc[zoom]
         h = RAD_TO_DEG * ( 2 * atan(exp(g)) - 0.5 * pi)
         return (f,h)

class SurveyChartPlugin(CMSPlugin):
    chart = models.ForeignKey(Chart)

def _get_db_type(connection):
    db = None
    if connection.settings_dict['ENGINE'] == "django.db.backends.sqlite3":
        db = "sqlite"
    elif connection.settings_dict['ENGINE'] == "django.db.backends.postgresql":
        db = "postgresql"
    elif connection.settings_dict['ENGINE'] == "django.db.backends.postgresql_psycopg2":
        db = "postgresql"
    elif connection.settings_dict['ENGINE'] == "django.db.backends.mysql":
        db = "mysql"
    return db

def _convert_query_paramstyle(connection, sql, params):
    db = _get_db_type(connection)
    if db == 'postgresql':
        return sql
    translations = dict([(p, ':'+p) for p in params.keys()])
    converted = sql % translations
    return converted
