from django.db import models

class Survey(models.Model):
    title = models.CharField(max_length=256)
    path = models.CharField(max_length=4096)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

class RuleType(models.Model):
    title = models.CharField(max_length=256)
    js_class = models.CharField(max_length=256)
    python_class = models.CharField(max_length=256)

    def __unicode__(self):
        return self.title

class QuestionDataType(models.Model):
    title = models.CharField(max_length=256)
    db_type = models.CharField(max_length=256)
    python_class = models.CharField(max_length=256)

    def __unicode__(self):
        return self.title

class VirtualOptionDataType(models.Model):
    title = models.CharField(max_length=256)
    question_data_type = models.ForeignKey(QuestionDataType)
    python_class = models.CharField(max_length=256)

    def __unicode__(self):
        return self.title

class Question(models.Model):
    survey = models.ForeignKey(Survey, db_index=True)
    starts_hidden = models.BooleanField()
    ordinal = models.IntegerField()
    title = models.CharField(max_length=256)
    description = models.TextField()
    type = models.CharField(max_length=256)
    data_type = models.ForeignKey(QuestionDataType)
    data_name = models.CharField(max_length=256)
    visual = models.CharField(max_length=256, blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['survey', 'ordinal']

class Option(models.Model):
    question = models.ForeignKey(Question, db_index=True)
    is_virtual = models.BooleanField()
    starts_hidden = models.BooleanField()
    ordinal = models.IntegerField()
    name = models.CharField(max_length=256)
    text = models.TextField()
    group = models.CharField(max_length=256)
    value = models.CharField(max_length=256)

    virtual_type = models.ForeignKey(VirtualOptionDataType, blank=True)
    virtual_inf = models.CharField(max_length=256, blank=True)
    virtual_sup = models.CharField(max_length=256, blank=True)
    virtual_regex = models.CharField(max_length=256, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['question', 'ordinal']

class Rule(models.Model):
    rule_type = models.ForeignKey(RuleType)
    subject_option = models.ForeignKey(Option, related_name='subject_option', db_index=True)
    object_question = models.ForeignKey(Question)
    object_option = models.ForeignKey(Option, related_name='object_option')

    def __unicode__(self):
        return '%s on option %s' % (self.rule_type)

