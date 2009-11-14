from django import forms
from epiweb.apps.survey.data import Survey, Section, Question
from epiweb.apps.survey.data.conditions import *
from epiweb.apps.survey.data.conditions import Compare

from epiweb.apps.survey import definitions as d

_ = lambda x: x

def create_field(question):
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

class SurveyReader:
    def __init__(self, survey):
        self.survey = survey
        self.initialized = False

    def read(self):
        if not self.initialized:
            self._analyze()
            self.initialized = True

    def _analyze(self):
        self._index = 0
        self.questions = []
        self.conditions = {}
        self.revindex = {}
        self._iterate(self.survey.rules)

    def _iterate(self, root, conditions=[]):
        for rule in root:
            t = type(rule).__name__
            if t == 'classobj' and issubclass(rule, d.Question):
                self._index += 1
                obj = rule()
                self.questions.append(obj)
                self.revindex[obj] = self._index
                self.conditions[obj] = conditions
            elif t == 'dict':
                cond = rule.keys()[0]
                sub = rule.values()[0]
                if type(sub).__name__ != 'tuple':
                    sub = rule.values()
                self._iterate(sub, conditions + [cond])


def generate_form(survey, values=None):
    sr = SurveyReader(survey)
    sr.read()

    if values:
        form = forms.Form(values)
    else:
        form = forms.Form()

    for question in sr.questions:
        form.fields[question.id] = create_field(question)

    return form

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

