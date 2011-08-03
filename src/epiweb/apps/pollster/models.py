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

SURVEY_TRANSLATION_STATUS_CHOICES = (
    ('DRAFT', 'Draft'),
    ('PUBLISHED', 'Published')
)

QUESTION_TYPE_CHOICES = (
    ('builtin', 'Builtin'),
    ('text', 'Open Answer'),
    ('single-choice', 'Single Choice'),
    ('multiple-choice', 'Multiple Choice'),
    ('matrix-select', 'Matrix Select'),
    ('matrix-entry', 'Matrix Entry'),
)

def _get_or_default(queryset, default=None):
    r = queryset[0:1]
    if r:
        return r[0]
    return default


class Survey(models.Model):
    parent = models.ForeignKey('self', db_index=True, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, default='')
    shortname = models.SlugField(max_length=255, default='')
    version = models.SlugField(max_length=255, default='')
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

    def get_last_partecipation_data(self, user_id, global_id):
        model = self.as_model()
        partecipation = model.objects\
            .filter(user=user_id)\
            .filter(global_id = global_id)\
            .order_by('-timestamp')\
            .values()
        return _get_or_default(partecipation)

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
    title = models.CharField(max_length=255, blank=True, default='')
    js_class = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

class QuestionDataType(models.Model):
    title = models.CharField(max_length=255, blank=True, default='')
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
    title = models.CharField(max_length=255, blank=True, default='')
    question_data_type = models.ForeignKey(QuestionDataType)
    js_class = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

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

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['survey', 'ordinal']

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

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            r = translation_survey.translationquestion_set.all().filter(question=self)
            default = TranslationQuestion(translation = translation_survey, question=self)
            self.translation_question = _get_or_default(r, default)

class QuestionRow(models.Model):
    question = models.ForeignKey(Question, related_name="row_set", db_index=True)
    ordinal = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, default='')

    translation_survey = None
    translation_row = None

    class Meta:
        ordering = ['question', 'ordinal']

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

    class Meta:
        ordering = ['question', 'ordinal']

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
    text = models.CharField(max_length=4095, blank=True, default='')
    group = models.CharField(max_length=255, blank=True, default='')
    value = models.CharField(max_length=255, default='')

    virtual_type = models.ForeignKey(VirtualOptionType, blank=True, null=True)
    virtual_inf = models.CharField(max_length=255, blank=True, default='')
    virtual_sup = models.CharField(max_length=255, blank=True, default='')
    virtual_regex = models.CharField(max_length=255, blank=True, default='')

    form = None
    translation_survey = None
    translation_option = None

    @property
    def translated_text(self):
        if self.translation and self.translation.text:
            return self.translation.text
        return self.text

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
    def translation(self):
        return self.translation_option

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

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            r = translation_survey.translationoption_set.all().filter(option=self)
            default = TranslationOption(translation = translation_survey, option=self)
            self.translation_option = _get_or_default(r, default)

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

# I18n models

class TranslationSurvey(models.Model):
    survey = models.ForeignKey(Survey, db_index=True)
    language = models.CharField(max_length=3, db_index=True)
    title = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=255, default='DRAFT', choices=SURVEY_TRANSLATION_STATUS_CHOICES)

    class Meta:
        ordering = ['survey', 'language']
        unique_together = ('survey', 'language')

    @models.permalink
    def get_absolute_url(self):
        return ('pollster_survey_translation_edit', [str(self.survey.id), self.language])

    def __unicode__(self):
        return "Translation(%s) for %s" % (self.language, self.survey)

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

    class Meta:
        ordering = ['translation', 'option']
        unique_together = ('translation', 'option')

    def as_form(self, data=None):
        class TranslationOptionForm(ModelForm):
            class Meta:
                model = TranslationOption
                fields = ['text']
        return TranslationOptionForm(data, instance=self, prefix="option_%s"%(self.id,))
