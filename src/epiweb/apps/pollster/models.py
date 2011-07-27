from django.db import models
from xml.etree import ElementTree
import re, warnings

class Survey(models.Model):
    parent = models.ForeignKey('self', db_index=True, blank=True, null=True)
    title = models.CharField(max_length=255, default='')
    shortname = models.SlugField(max_length=255, default='')
    version = models.SlugField(max_length=255, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def create_from_xml(self, xmlstring):
        self.update_from_xml(xmlstring)

    def update_from_xml(self, xmlstring):
        # ElementTree does not like being passed unicode objects
        xmlstring = '<?xml version="1.0" encoding="UTF-8"?>'+xmlstring.encode('utf-8')
        root = ElementTree.XML(xmlstring)

        self.title = root.find('h1').text or ''
        self.shortname = root.find('h1').get('data-shortname') or ''
        self.version = root.find('h1').get('data-version') or ''
        self.save()

        idmap = {}
        question_ordinal = 1
        question_xrules = []
        for wrapper in root.findall('div'):
            if 'question-wrapper' not in wrapper.get('class'):
                continue
            xquestion = [i for i in wrapper if 'question' in i.get('class')][0]
            question = self.update_question_from_xml(idmap, xquestion, question_ordinal)
            question_ordinal += 1

            column_ordinal = 1
            xcolumns = [ul for ul in xquestion.findall('ul') if 'columns' in ul.get('class')] or [[]]
            for xcolumn in xcolumns[0]:
                self.update_column_from_xml(idmap, question, xcolumn, column_ordinal)
                column_ordinal += 1

            row_ordinal = 1
            xrows = [ul for ul in xquestion.findall('ul') if 'rows' in ul.get('class')] or [[]]
            for xrow in xrows[0]:
                self.update_row_from_xml(idmap, question, xrow, row_ordinal)
                row_ordinal += 1

            option_ordinal = 1
            xoptions = [ul for ul in xquestion.findall('ul') if 'choices' in ul.get('class')] or [[]]
            for xoption in xoptions[0]:
                self.update_option_from_xml(idmap, question, xoption, option_ordinal)
                option_ordinal += 1

            xrules = [i for i in wrapper if 'rules' in i.get('class')][0]
            question_xrules.append((question, xrules))

        # After generating correct IDs for all questions and options we process
        # the rules by iterating again the XML tree.

        for question, xrules in question_xrules:
            for xrule in xrules:
                self.update_rule_from_xml(idmap, question, xrule)

        self.save()

    def update_question_from_xml(self, idmap, root, ordinal):
        # Extract question ID and load corresponding question; if it does not exists
        # insert and empty question to generate it. In both cases we have a question
        # to fill with options and rules.
        data_type = root.get('data-data-type')
        open_option_data_type = root.get('data-open-option-data-type')
        tags = root.get('data-tags')
        regex = None
        if root.find('input') is not None:
            regex = root.find('input').get('pattern')
        error_message = ([e.text for e in root.findall('p') if 'error-message' in e.get('class', '')] + [None]) [0]
        data_name = [e.text for e in root.findall('div') if 'info' in e.get('class', '')][0]
        title = [e.text for e in root.findall('p/span') if 'title' in e.get('class', '')][0]
        hidden = 'starts-hidden' in (root.get('class') or '')
        mandatory = 'mandatory' in (root.get('class') or '')
        deleted = 'deleted' in (root.get('class') or '')
        description = ''
        xdescription = root.find('p')
        if xdescription is not None:
            description = (xdescription[-1].tail or '').strip()

        temp_id = root.get('id') or ''
        match = re.match('^question-(\d+)$', temp_id)

        if deleted:
            Question.objects.filter(id = int(match.group(1))).delete()
            question = None
        elif match:
            question = Question.objects.get(id = int(match.group(1)))
            question.data_name = data_name or ''
            question.title = title or ''
            question.description = description or ''
            question.tags = tags or ''
            question.regex = regex or ''
            question.error_message = error_message or ''
            question.starts_hidden = hidden
            question.is_mandatory = mandatory
            question.ordinal = ordinal
            if data_type:
                question.data_type = QuestionDataType.objects.get(id = data_type)
            if open_option_data_type:
                question.open_option_data_type = QuestionDataType.objects.get(id = open_option_data_type)
            question.save()
        else:
            question_type = root.get('data-question-type')
            question = Question()
            question.survey = self
            question.type = question_type
            question.data_name = data_name or ''
            question.title = title or ''
            question.description = description or ''
            question.tags = tags or ''
            question.regex = regex or ''
            question.error_message = error_message or ''
            question.starts_hidden = hidden
            question.is_mandatory = mandatory
            question.ordinal = ordinal
            if data_type:
                question.data_type = QuestionDataType.objects.get(id = data_type)
            else:
                question.data_type = QuestionDataType.objects.get(id = 1)
            if open_option_data_type:
                question.open_option_data_type = QuestionDataType.objects.get(id = open_option_data_type)
            question.save()
        idmap[temp_id] = question and question.id
        return question

    def update_column_from_xml(self, idmap, question, root, ordinal):
        temp_id = root.get('id') or ''
        match = re.match('^column-(\d+)$', temp_id)
        deleted = 'deleted' in (root.get('class') or '')
        if deleted or question is None:
            QuestionColumn.objects.filter(id = int(match.group(1))).delete()
            column = None
        else:
            title = [e.text for e in root.findall('span') if 'title' in e.get('class', '')][0]
            if match:
                column = QuestionColumn.objects.get(id = int(match.group(1)))
                column.title = title or ''
                column.ordinal = ordinal
                column.save()
            else:
                column = QuestionColumn()
                column.question = question
                column.title = title or ''
                column.ordinal = ordinal
                column.save()
        idmap[temp_id] = column and column.id
        return column

    def update_row_from_xml(self, idmap, question, root, ordinal):
        temp_id = root.get('id') or ''
        match = re.match('^row-(\d+)$', temp_id)
        deleted = 'deleted' in (root.get('class') or '')
        if deleted or question is None:
            QuestionRow.objects.filter(id = int(match.group(1))).delete()
            row = None
        else:
            title = [e.text for e in root.findall('span') if 'title' in e.get('class', '')][0]
            if match:
                row = QuestionRow.objects.get(id = int(match.group(1)))
                row.title = title or ''
                row.ordinal = ordinal
                row.save()
            else:
                row = QuestionRow()
                row.question = question
                row.title = title or ''
                row.ordinal = ordinal
                row.save()
        idmap[temp_id] = row and row.id
        return row

    def update_option_from_xml(self, idmap, question, root, ordinal):
        # If we have an <input> tag, then this is a real option, else it is
        # a virtual option and we read the range/regexp data directly from
        # the <li> element. We also look for the option id, to decide if this
        # is an old option to update or a new one to create.
        temp_id = root.get('id') or ''
        match = re.match('^option-(\d+)$', temp_id)
        xinput = root.find('input')
        hidden = 'starts-hidden' in (root.get('class') or '')
        is_open = 'open' in (root.get('class') or '')
        deleted = 'deleted' in (root.get('class') or '')
        if deleted or question is None:
            Option.objects.filter(id = int(match.group(1))).delete()
            option = None
        elif xinput is not None:
            text = root.find('label').text
            value = xinput.get('value')
            if match:
                option = Option.objects.get(id = int(match.group(1)))
                option.starts_hidden = hidden
                option.is_open = is_open
                option.text = text or ''
                option.value = value or ''
                option.ordinal = ordinal
                option.name = "%s_%s" % (question.data_name, option.id)
                option.save()
            else:
                option = Option()
                option.question = question
                option.is_virtual = False
                option.starts_hidden = hidden
                option.is_open = is_open
                option.text = text or ''
                option.value = value or ''
                option.ordinal = ordinal
                option.save()
                # to update the name we need the generated option id.
                option.name = "%s_%s" % (question.data_name, option.id)
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
                option.name = "%s_%s" % (question.data_name, option.id)
                option.save()
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
                option.save()
                # to update the name we need the generated option id.
                option.name = "%s_%s" % (question.data_name, option.id)
                option.save()
        idmap[temp_id] = option and option.id
        return option

    def update_rule_from_xml(self, idmap, question, root):
        temp_id = root.get('id') or ''
        match = re.match('^rule-(\d+)$', temp_id)
        type_id = root.get('data-type')
        subject_option_id = root.get('data-subject-option')
        object_question_id = root.get('data-object-question')
        object_option_ids = (root.get('data-object-options') or '').split()
        deleted = 'deleted' in (root.get('class') or '')

        if not deleted and not (type_id and subject_option_id and object_question_id):
            warnings.warn('unable to create rule in question %s (trigger %s, question %s)' % (question.id, subject_option_id, object_question_id))
            return None

        if deleted or question is None or Survey.get_option_id(idmap, subject_option_id) is None or Survey.get_question_id(idmap, object_question_id) is None:
            Rule.objects.filter(id = int(match.group(1))).delete()
            rule = None
        elif match:
            rule = Rule.objects.get(id = int(match.group(1)))
            rule.rule_type = RuleType.objects.get(id = int(type_id))
            rule.subject_question = question
            rule.subject_option = Option.objects.get(id = Survey.get_option_id(idmap, subject_option_id))
            rule.object_question = Question.objects.get(id = Survey.get_question_id(idmap, object_question_id))
            rule.save()
            rule.object_options.clear()
            for id in [Survey.get_option_id(idmap, object_option_id) for object_option_id in object_option_ids]:
                if id is not None:
                    rule.object_options.add(Option.objects.get(id = id))
            rule.save()
        else:
            rule = Rule()
            rule.rule_type = RuleType.objects.get(id = int(type_id))
            rule.subject_question = question
            rule.subject_option = Option.objects.get(id = Survey.get_option_id(idmap, subject_option_id))
            rule.object_question = Question.objects.get(id = Survey.get_question_id(idmap, object_question_id))
            rule.save()
            rule.object_options.clear()
            for id in [Survey.get_option_id(idmap, object_option_id) for object_option_id in object_option_ids]:
                if id is not None:
                    rule.object_options.add(Option.objects.get(id = id))
            rule.save()
        return rule

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
    subject_option = models.ForeignKey(Option, related_name='subject_of_rules', limit_choices_to = {'question': subject_question}, blank=True, null=True)
    object_question = models.ForeignKey(Question, related_name='object_of_rules', blank=True, null=True)
    object_options = models.ManyToManyField(Option, related_name='object_of_rules', limit_choices_to = {'question': object_question})

    def js_class(self):
        return self.rule_type.js_class

    def __unicode__(self):
        return '%s on question %s' % (self.rule_type, self.subject_question.id)

