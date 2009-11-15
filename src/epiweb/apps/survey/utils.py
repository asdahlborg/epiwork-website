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

