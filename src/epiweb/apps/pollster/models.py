from django.db import models

class Survey(models.Model):
    title = models.CharField(max_length=255, unique=True)
    path = models.CharField(max_length=4096)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

class RuleType(models.Model):
    title = models.CharField(max_length=255, unique=True)
    js_class = models.CharField(max_length=255)
    python_class = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

class QuestionDataType(models.Model):
    title = models.CharField(max_length=255, unique=True)
    db_type = models.CharField(max_length=255)
    python_class = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

class VirtualOptionType(models.Model):
    title = models.CharField(max_length=255)
    question_data_type = models.ForeignKey(QuestionDataType)
    python_class = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

class Question(models.Model):
    survey = models.ForeignKey(Survey, db_index=True)
    starts_hidden = models.BooleanField(default=False)
    ordinal = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=255)
    data_type = models.ForeignKey(QuestionDataType)
    data_name = models.CharField(max_length=255)
    visual = models.CharField(max_length=255, blank=True, null=True)

    @property
    def is_text(self):
        return self.type == 'text'

    @property
    def is_single_choice(self):
        return self.type == 'single-choice'

    @property
    def is_multiple_choice(self):
        return self.type == 'multiple-choice'

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['survey', 'ordinal']

class Option(models.Model):
    question = models.ForeignKey(Question, db_index=True)
    is_virtual = models.BooleanField(default=False)
    starts_hidden = models.BooleanField(default=False)
    ordinal = models.IntegerField()
    name = models.CharField(max_length=255)
    text = models.TextField()
    group = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=255)

    virtual_type = models.ForeignKey(VirtualOptionType, blank=True, null=True)
    virtual_inf = models.CharField(max_length=255, blank=True, null=True)
    virtual_sup = models.CharField(max_length=255, blank=True, null=True)
    virtual_regex = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['question', 'ordinal']

class Rule(models.Model):
    rule_type = models.ForeignKey(RuleType)
    subject_option = models.ForeignKey(Option, related_name='subject_option', db_index=True)
    object_question = models.ForeignKey(Question)
    object_option = models.ForeignKey(Option, related_name='object_option')

    def js_object_option_id(self):
        if self.object_option:
            return self.object_option.id
        return 'null'

    def js_class(self):
        return self.rule_type.js_class

    def __unicode__(self):
        return '%s on option %s' % (self.rule_type)

