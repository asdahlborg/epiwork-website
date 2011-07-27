from django.db import models
from xml.etree import ElementTree
import re, warnings
from . import parser

class Survey(models.Model):
    parent = models.ForeignKey('self', db_index=True, blank=True, null=True)
    title = models.CharField(max_length=255, default='')
    shortname = models.SlugField(max_length=255, default='')
    version = models.SlugField(max_length=255, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_question_id(idmap, idstr):
        return idmap[idstr]

    @staticmethod
    def get_option_id(idmap, idstr):
        return idmap[idstr]

    @models.permalink
    def get_absolute_url(self):
        return ('pollster_survey_edit', [str(self.id)])

    def __unicode__(self):
        return "#%d %s" % (self.id, self.title)

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
    type = models.CharField(max_length=255)
    data_type = models.ForeignKey(QuestionDataType)
    open_option_data_type = models.ForeignKey(QuestionDataType, related_name="questions_with_open_option", null=True, blank=True)
    data_name = models.CharField(max_length=255)
    visual = models.CharField(max_length=255, blank=True, default='')
    tags = models.CharField(max_length=255, blank=True, default='')
    regex = models.CharField(max_length=1023, blank=True, default='')
    error_message = models.TextField(blank=True, default='')

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

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['question', 'ordinal']

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

