from django.db import models
from xml.etree import ElementTree
import re

class Survey(models.Model):
    title = models.CharField(max_length=255, default='')
    path = models.CharField(max_length=4096)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def create_from_xml(self, xmlstring):
        self.update_from_xml(xmlstring)

    def update_from_xml(self, xmlstring):
        root = ElementTree.XML(xmlstring)

        self.title = root.find('h1').text or ''
        self.path = 'FIXME'
        self.save()

        idmap = {}
        question_ordinal = 1
        for wrapper in root.findall('div'):
            if 'question-wrapper' not in wrapper.get('class'):
                continue
            option_ordinal = 1
            xquestion = [i for i in wrapper if 'question' in i.get('class')][0]
            question = self.update_question_from_xml(idmap, xquestion, question_ordinal)
            question_ordinal += 1

            for xoption in xquestion.findall('form/ul/li'):
                self.update_option_from_xml(idmap, question, xoption, option_ordinal)
                option_ordinal += 1

        # After generating correct IDs for all questions and options we process
        # the rules by iterating again the XML tree.

        for wrapper in root.findall('div'):
            if 'question-wrapper' not in wrapper.get('class'):
                continue
            xrules = [i for i in wrapper if 'rules' in i.get('class')][0]
            for xrule in xrules:
                self.update_rule_from_xml(idmap, question, xrule)

        self.save()

    def update_question_from_xml(self, idmap, root, ordinal):
        # Extract question ID and load corresponding question; if it does not exists
        # insert and empty question to generate it. In both cases we have a question
        # to fill with options and rules.
        data_type = root.get('data-data-type')
        data_name = [e.text for e in root.findall('div') if 'info' in e.get('class')][0]
        title = [e.text for e in root.findall('p/span') if 'title' in e.get('class')][0]
        hidden = 'starts-hidden' in (root.get('class') or '')
        description = ''
        xdescription = root.find('p')
        if xdescription != None:
            description = (xdescription[-1].tail or '').strip()

        temp_id = root.get('id') or ''
        match = re.match('^question-(\d+)$', temp_id)
        if match:
            question = Question.objects.get(id = int(match.group(1)))
            question.data_name = data_name or ''
            question.title = title or ''
            question.description = description or ''
            question.starts_hidden = hidden
            question.ordinal = ordinal
            if data_type:
                question.data_type = QuestionDataType.objects.get(id = data_type)
            question.save()
        else:
            question_type = root.get('data-question-type')
            question = Question()
            question.survey = self
            question.type = question_type
            question.data_name = data_name or ''
            question.title = title or ''
            question.description = description or ''
            question.starts_hidden = hidden
            question.ordinal = ordinal
            if data_type:
                question.data_type = QuestionDataType.objects.get(id = data_type)
            else:
                question.data_type = QuestionDataType.objects.get(id = 1)
            question.save()
            idmap[temp_id] = question.id
        return question

    def update_option_from_xml(self, idmap, question, root, ordinal):
        # If we have an <input> tag, then this is a real option, else it is
        # a virtual option and we read the range/regexp data directly from
        # the <li> element. We also look for the option id, to decide if this
        # is an old option to update or a new one to create.
        temp_id = root.get('id') or ''
        match = re.match('^option-(\d+)$', temp_id)
        xinput = root.find('input')
        hidden = 'starts-hidden' in (root.get('class') or '')
        if xinput != None:
            text = root.find('label').text
            value = xinput.get('value')
            if match:
                option = Option.objects.get(id = int(match.group(1)))
                option.starts_hidden = hidden
                option.text = text or ''
                option.value = value or ''
                option.ordinal = ordinal
            else:
                option = Option()
                option.question = question
                option.is_virtual = False
                option.starts_hidden = hidden
                option.text = text or ''
                option.value = value or ''
                option.ordinal = ordinal
                idmap[temp_id] = question.id
            option.save()
        else:
            type_id = root.get('data-type')
            value = root.get('data-value')
            inf = root.get('data-inf')
            sup = root.get('data-sup')
            regex = root.get('data-regex')
            if match:
                option = Option.objects.get(id = int(match.group(1)))
                option.virtual_type = VirtualOptionType.objects.get(id=int(type_id))
                option.virtual_inf = inf or ''
                option.virtual_sup = sup or ''
                option.virtual_regex = regex or ''
                option.value = value or ''
                option.starts_hidden = hidden
                option.ordinal = ordinal
            else:
                option = Option()
                option.question = question
                option.is_virtual = True
                option.virtual_inf = inf or ''
                option.virtual_sup = sup or ''
                option.virtual_regex = regex or ''
                option.value = value or ''
                option.starts_hidden = hidden
                option.ordinal = ordinal
                idmap[temp_id] = question.id
            option.save()
        # to update the name we need the generated option id.
        option.name = "%s_%s" % (question.data_name, option.id)
        return option

    def update_rule_from_xml(self, idmap, question, root):
        temp_id = root.get('id') or ''
        match = re.match('^rule-(\d+)$', temp_id)
        type_id = root.get('data-type')
        subject_option_id = root.get('data-trigger')
        object_question_id = root.get('data-question')
        if type_id and subject_option_id and object_question_id:
            if match:
                rule = Rule.objects.get(id = int(match.group(1)))
                rule.rule_type = RuleType.objects.get(id = int(type_id))
                rule.subject_option = Option.objects.get(id = Survey.get_option_id(idmap, subject_option_id))
                rule.object_question = Question.objects.get(id = Survey.get_question_id(idmap, object_question_id))
            else:
                rule = Rule()
                rule.rule_type = RuleType.objects.get(id = int(type_id))
                rule.subject_option = Option.objects.get(id = Survey.get_option_id(idmap, subject_option_id))
                rule.object_question = Question.objects.get(id = Survey.get_question_id(idmap, object_question_id))
            rule.save()
            return rule
        raise RuntimeError('unable to create rule for question %s' % (question.id))

    @staticmethod
    def get_question_id(idmap, idstr):
        match = re.match('^question-(\d+)$', idstr)
        if match:
            return int(match.group(1))
        else:
            return idmap[idstr]

    @staticmethod
    def get_option_id(idmap, idstr):
        match = re.match('^option-(\d+)$', idstr)
        if match:
            return int(match.group(1))
        else:
            return idmap[idstr]

    @models.permalink
    def get_absolute_url(self):
        return ('pollster_survey_edit', [str(self.id)])

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
    title = models.CharField(max_length=255, default='')
    description = models.TextField(blank=True, default='')
    type = models.CharField(max_length=255)
    data_type = models.ForeignKey(QuestionDataType)
    data_name = models.CharField(max_length=255)
    visual = models.CharField(max_length=255, blank=True, default='')

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
    def subject_of_rules(self):
        return Rule.objects.filter(subject_option__question=self)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['survey', 'ordinal']

class Option(models.Model):
    question = models.ForeignKey(Question, db_index=True)
    is_virtual = models.BooleanField(default=False)
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
    subject_option = models.ForeignKey(Option, related_name='subject_of_rules', db_index=True, blank=True, null=True)
    object_question = models.ForeignKey(Question, related_name='object_of_rules', blank=True, null=True)
    object_option = models.ForeignKey(Option, related_name='object_of_rules', blank=True, null=True)

    def js_object_option_id(self):
        if self.object_option:
            return self.object_option.id
        return 'null'

    def js_class(self):
        return self.rule_type.js_class

    def __unicode__(self):
        return '%s on option %s' % (self.rule_type)

