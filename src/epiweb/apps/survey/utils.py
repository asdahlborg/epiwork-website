from django import forms
from epiweb.apps.survey.data import Survey, Section, Question
from epiweb.apps.survey.data.conditions import *
from epiweb.apps.survey.data.conditions import Compare

from epiweb.apps.survey import definitions as d

_ = lambda x: x

def generate_js_helper(section):
    obj = 's'
    lines = []
    ids = []
    for question in section.questions:
        ids.append(question.id)
        if question.condition is not None:
            lines.append('%s.eval["%s"] = function() { return %s; }' % (obj, question.id, 
                            create_js_statement(question.condition)))
        else:
            lines.append('%s.eval["%s"] = function() { return true; }' % (obj, question.id))

    return """
(function() {
var q = [%(id)s];
var s = new Survey();
s.set_questions(q);
s.eval = [];
%(condition)s
s.init();
})();
""" % { 
        'condition': "\n".join(lines), 
        'id': ", ".join(map(lambda x: "'%s'" % x, ids)) 
    }
        

def get_intake_value(id):
    return "true"

def create_js_statement(v, obj='s'):
    if isinstance(v, Q):
        return "%s.Q('%s')" % (obj, v.id)
    elif isinstance(v, Intake):
        return get_intake_value(v.id)
    elif isinstance(v, OneOf):
        options = map(lambda x: str(x), v.options)
        return "%s.OneOf(%s, [%s])" % (obj, create_js_statement(v.a), ", ".join(options))
    elif isinstance(v, NotEmpty):
        return "%s.NotEmpty(%s)" % (obj, create_js_statement(v.a))
    elif isinstance(v, Compare):
        sa = create_js_statement(v.a)
        sb = create_js_statement(v.b)
        _op = {
            'and': '&&', 'or': '||',
            'eq': '==',  'ne': '!=',
            'lt': '<',   'le': '<=',
            'gt': '>',   'ge': '>='
        }
        return "(%s) %s (%s)" % (sa, _op[v.op], sb)
    elif isinstance(v, bool):
        if v: return "true"
        else: return "false"
    else:
        return v

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
        lines += self._create_affected_list()
        lines += self._create_rules()
        lines.append("s.init();")
        lines.append("})('%s', '%s');" % (self.container, self.prefix))
        self.js = "\n".join(lines)

    def _create_affected_list(self):
        lines = []
        lines.append("s.affected = {};")
        for question in self.survey.questions:
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
            lines.append("s.rule['%s'] = function() { return %s };" % (question.id, rule))

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

class SurveyFormHelper:
    def __init__(self, survey):
        self.survey = survey
        self.form_class = None

    def create_form(self, data=None):
        if self.form_class is None:
            self._generate_form()

        if data is None:
            return self.form_class()
        else:
            return self.form_class(data)

    def _generate_form(self):
        fields = {}
        for question in self.survey.questions:
            fields[question.id] = self._create_field(question)
        self.form_class = type('SurveyForm', (forms.Form, object), fields)

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
            field = forms.DateField(input_formats='%m/%d/%y')
    
        else:
            field = forms.CharField()
    
        field.label = question.question
        field.required = False
    
        return field

