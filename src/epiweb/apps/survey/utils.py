from django import forms
from django.forms.util import ErrorList

from epiweb.apps.survey.data import Survey, Section, Question
from epiweb.apps.survey.data.conditions import *
from epiweb.apps.survey.data.conditions import Compare

from epiweb.apps.survey import definitions as d

_ = lambda x: x

class JavascriptHelper:
    def __init__(self, survey, container_id='survey', question_id_prefix="q_"):
        self.survey = survey
        self.container = container_id
        self.prefix = question_id_prefix
        self.js = None

    def get_javascript(self):
        if self.js is None:
            self._generate_javascript()
        return self.js

    def _generate_javascript(self):
        lines = []
        lines.append("(function(container, prefix) {")
        lines.append("var s = new Survey(container, prefix);")
        lines += self._create_question_list()
        lines += self._create_allow_blank_condition()
        lines += self._create_affected_list()
        lines += self._create_rules()
        lines.append("s.init();")
        lines.append("})('%s', '%s');" % (self.container, self.prefix))
        self.js = "\n".join(lines)

    def _create_question_list(self):
        return ["s.qids = [%s];" % ", ".join(map(lambda x: "'%s'" % x.id, self.survey.questions))]

    def _create_allow_blank_condition(self):
        lines = []
        lines.append('s.blank = {};')
        for question in self.survey.questions:
            if question.blank:
                lines.append("s.blank['%s'] = true;" % question.id)
        return lines

    def _create_affected_list(self):
        lines = []
        lines.append("s.affected = {};")
        for question in self.survey.questions:
            if len(self.survey.affected[question]) > 0:
                lines.append("s.affected['%s'] = new Array(%s);" % (question.id,
                    ', '.join(map(lambda x: "'%s'" % x.id, self.survey.affected[question]))))
        return lines
        
    def _create_rules(self):
        lines = []
        lines.append("s.rule = {};")

        for question in self.survey.questions:
            rule = self._create_rule(self.survey.conditions[question])
            if rule == '':
                rule = 'true'
            lines.append("s.rule['%s'] = function() { return %s; };" % (question.id, rule))

        return lines

    def _convert_value(self, value):
        t = type(value).__name__
        if t == 'tuple':
            return "(%s)" % self._create_rule(value)
        elif t == 'instance': 
            if isinstance(value, d.Question):
                return "s.Value('%s')" % value.id
            elif isinstance(value, d.Items):
                return "[%s]" % ', '.join(map(lambda x: self._convert_value(x),
                                                value.values))
            elif isinstance(value, d.Profile):
                return "s.Profile('%s')" % value.name
        elif t == 'classobj' and issubclass(value, d.Value):
            name = value.__name__
            if name == 'Empty':
                return 's.Empty()'

        elif t in ['int', 'float']:
            return str(value)
        elif t == 'str':
            # FIXME escape the value
            return '"%s"' % value

        # TODO
        raise RuntimeError()

    def _add_operator(self, op, a, b):
        map = {
            'is': 's.Is',
            'is-not': 's.IsNot',
            'is-in': 's.IsIn'
        }
        return '%s(%s, %s)' % (map.get(op, map['is']), a, b)

    def _create_rule(self, conditions):
        rules = []
        for cond in conditions:
            a = cond[0]
            b = cond[2]

            a = self._convert_value(a)
            b = self._convert_value(b)

            rules.append(self._add_operator(cond[1], a, b))

        return " && ".join(map(lambda x: '(%s)' % x, rules))

class SurveyFormBase(forms.Form):
    def __init__(self, *args, **kwargs):
        self._survey = kwargs['survey']
        del kwargs['survey']
        super(SurveyFormBase, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data
        valid_ids = cleaned_data.keys()

        for question in self._survey.questions:
            if question.id not in valid_ids:
                continue
            visible = self._evaluate_condition(question)
            value = self._get_value(question)
            if visible and len(value) == 0 and not question.blank:
                msg = _(u'Please answer this question.')
                self._errors[question.id] = ErrorList([msg])
                del cleaned_data[question.id]

        return cleaned_data

    def _evaluate_condition(self, question):
        for cond in self._survey.conditions[question]:
            if not self._evaluate(cond):
                return False
        return True

    def _evaluate(self, cond):
        a = cond[0]
        op = cond[1]
        b = cond[2]
    
        va = self._get_value(a)
        vb = self._get_value(b)

        if op == 'is':
            return va == vb
        elif op == 'is-not':
            return va != vb
        elif op == 'is-in':
            for ia in va:
                if ia not in vb:
                    return False
            return True

        # TODO
        raise RuntimeError()

    def _get_profile(self, name):
        # TODO
        return [1]

    def _get_value(self, value):
        t = type(value).__name__    
        if t == 'tuple':
            return self._evaluate(value)
        elif t == 'instance':
            if isinstance(value, d.Question):
                res = self.cleaned_data.get(value.id, None)
                if res == None:
                    res = []
                elif value.type in ['option-single']:
                    res = res.strip()
                    if res == '':
                        res = []
                    else:
                        res = [int(res)]
                elif value.type in ['option-multiple']:
                    res = map(lambda x: int(x), res)
                else:
                    res = [res]

                return res
            elif isinstance(value, d.Items):
                return value.values
            elif isinstance(value, d.Profile):
                return self._get_profile(value.name)
        elif t == 'classobj' and issubclass(value, d.Value):
            name = value.__name__
            if name == 'Empty':
                return []
        elif t == 'list':
            return value
        else:
            return [value]

        # TODO
        raise RuntimeError()

class SurveyFormHelper:
    def __init__(self, survey):
        self.survey = survey
        self.form_class = None

    def create_form(self, data=None):
        if self.form_class is None:
            self._generate_form()

        if data is None:
            return self.form_class(survey=self.survey)
        else:
            return self.form_class(data, survey=self.survey)

    def _generate_form(self):
        fields = {}
        for question in self.survey.questions:
            fields[question.id] = self._create_field(question)
        self.form_class = type('SurveyForm', (SurveyFormBase, object), fields)

    def _create_field(self, question):
        if question.type == 'yes-no':
            field = forms.ChoiceField(widget=forms.RadioSelect,
                                      choices=[('yes', _('Yes')), ('no', _('No'))])
    
        elif question.type == 'option-multiple':
            field = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                              choices=zip(range(0, len(question.options)), question.options))
    
        elif question.type == 'option-single':
            field = forms.ChoiceField(widget=forms.RadioSelect,
                                      choices=zip(range(0, len(question.options)), question.options))
    
        elif question.type == 'date':
            print "=== date"
            field = forms.DateField(input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y', '%d-%m-%y', '%d-%m-%Y', '%b %d %Y', '%b %d, %Y', '%d %b %Y', '%d %b, %Y', '%B %d %Y', '%B %d, %Y', '%d %B %Y', '%d %B, %Y'])
    
        else:
            field = forms.CharField()
    
        field.label = question.question
        field.required = False
    
        return field

