from pprint import pprint
import simplejson as json
from collections import defaultdict
from inspect import isclass

from django import forms
from django.forms.util import ErrorList
from . import spec as d
from .forms import ( AdviseField, DatePickerWidget, MonthYearField,
                     PostCodeField, DateOrOptionField,
                     TableOptionsSingleField, TableOfSelectsField)

def parse_specification(spec, survey_class='Survey'):
    vars = {'d': d}
    exec(spec, vars)

    klass = vars[survey_class]
    return klass

class Specification(object):
    def __init__(self, survey):
        '''
        @param spec.Survey survey
        '''
        self.survey = survey
        self._id_mapping = None
        self._questions = None
        self._modifier = None
        self._modified = None
        self._responses = None
        self._profiles = None
        self._prefills = None
        self._conditions = None

        d.validate_rules(survey.rules)

    def get_questions(self, root=None, id_mapping={}):
        if self._questions is not None and root is None:
            return self._questions

        if root is None:
            root = self.survey.rules

        questions = []
        for item in root:
            if isinstance(item, d.Branch):
                questions += self.get_questions(item.rules, id_mapping)
            elif issubclass(item, d.Question):
                obj = item()
                questions.append(obj)
                id_mapping.update({item.__name__: obj.id})

        if root == self.survey.rules:
            self._questions = questions
            self._id_mapping = id_mapping

        return questions

    questions = property(get_questions)

    def get_id_mapping(self):
        self.get_questions()
        return self._id_mapping

    id_mapping = property(get_id_mapping)

    def get_usage(self, name):
        res = {}
        for question in self.questions:
            modifier = question.get_usage(name)
            if len(modifier) > 0:
                res[question.id] = modifier

        return res

    def get_modifier(self):
        if self._modifier is None:
            self._modifier = self.get_usage('question')
        return self._modifier

    def get_modified(self):
        if self._modified is not None:
            return self._modified

        res = defaultdict(list)
        for question, modifier in self.get_modifier().items():
            for mod in modifier:
                res[mod].append(question)

        self._modified = dict(res)
        return self._modified

    def get_profiles(self):
        if self._profiles is None:
            usage = self.get_usage('profile')
            ids = list(set([id for items in usage.values() for id in items]))
            self._profiles = ids
        return self._profiles

    def get_responses(self):
        if self._responses is None:
            usage = self.get_usage('response')
            response_ids = list(set([id for items in usage.values() for id in items]))

            keys = self.survey.prefill.keys()
            self.get_questions() # make sure the mapping is finished
            prefill_ids = [self._id_mapping[key.__name__] for key in keys]

            ids = response_ids + prefill_ids

            self._responses = ids
        return self._responses

    def get_conditions(self):
        if self._conditions is None:
            res = {}
            for question in self.questions:
                condition = question.get_condition()
                res[question.id] = condition
            self._conditions = res
        return self._conditions

    def get_prefills(self):
        if self._prefills is None:
            res = {}
            self.get_questions() # make sure the mapping is finished
            for key, value in self.survey.prefill.items():
                id = self._id_mapping[key.__name__]
                res[id] = value
            self._prefills = res
        return self._prefills

def get_template_context(spec, context):
    """Get and return a context containing the date and responses to the last
    completed survey, as well a other contextual information required by the
    questionnaires.
    """
    from utils import get_last_response
    lrdir = get_last_response(context.user) or {}

    from models import LastResponse, epoch
    lr = LastResponse.objects.get(user=context.user)
    if ( lr.participation
         and lr.participation.date
         and not lr.participation.date == epoch() ):
       lrdir['DATE'] = lr.participation.date

    def season(delta=0):
        from datetime import datetime
        now = datetime.now()
        year = now.year + delta
        if now.month > 6:
            return '%d-%d' % (year, year+1)
        else:
            return '%d-%d' % (year-1, year)

    d = { 'LAST_SURVEY': lrdir,
          'SEASON': season(),
          'LAST_SEASON': season(-1) }

    return d 

class SurveyFormBase(forms.Form):
    def clean(self):
        from copy import copy
        data = copy(self.cleaned_data)
        values = copy(data)
        values.update({'+id': self.spec.id_mapping})
        values.update({'+p': self.context.profile.values})
        values.update({'+r': self.context.response.values})

        # from pprint import pprint
        # pprint(self.spec.get_modifier())
        # pprint(self.spec.get_modified())
        # pprint(values)
        # pprint(self._errors)

        for question in self.spec.questions:
            # print 'Cond [%s]: %s' % (question.id, question.get_condition())
            # print '- js:', question.get_condition().js
            # print '- modifier:', question.get_modifier()
            # print '- visible:', question.visible(values)
            if not question.visible(values):
                data[question.id] = None
                # print 'DELETE', question.id
                if question.id in self._errors.keys():
                    del self._errors[question.id]
            elif not data.has_key(question.id):
                self._errors[question.id] = ErrorList(['Please correct the answers.'])
            elif self._is_empty(data, question) and not question.blank:
                self._errors[question.id] = ErrorList(['Please answer this question.'])
                del data[question.id]

            if data.has_key(question.id):
                field = self.fields[question.id]
                if hasattr(field, 'clean_all'):
                    try:
                        value = field.clean_all(question.id, data)
                        data[question.id] = value
                    except forms.ValidationError:
                        self._errors[question.id] = ErrorList(['Please correct the answers.'])
                        del data[question.id]
        cond = self.spec.questions[0].get_condition()

        return data

    def _is_empty(self, data, question):
        value = data[question.id]
        if type(value) in [list, set, tuple]:
            if len(value) == 0:
                return True
        else:
            value = [value]
        return all([val in [None, ''] for val in value])

class SurveyContext(object):
    def __init__(self, user, profile, response):
        self.user = user
        self.profile = profile
        self.response = response

class ProfileContext(object):
    def __init__(self, survey_user):
        self.user = survey_user
        self._profile = None

    def get_profile(self):
        if self._profile is None:
            from . import utils
            self._profile = utils.get_user_profile(self.user)
        return self._profile
    profile = property(get_profile)

    def get_values(self):
        initial = self.profile
        if initial is None:
            initial = {}
        res = defaultdict(lambda: None)
        res.update(initial)
        return res

    values = property(get_values)

class ResponseContext(object):
    def __init__(self, survey_user):
        self.user = survey_user
        self._response = None

    def get_response(self):
        if self._response is None:
            from . import utils
            self._response = utils.get_last_response(self.user)
        return self._response
    response = property(get_response)

    def get_values(self):
        initial = self.response
        if initial is None:
            initial = {}
        res = defaultdict(lambda: None)
        res.update(initial)
        return res
    values = property(get_values)

def get_survey_context(survey_user):
    profile = ProfileContext(survey_user)
    response = ResponseContext(survey_user)
    return SurveyContext(survey_user, profile, response)

class TextTemplate(object):
    def __init__(self, form, question):
        self.form = form
        self.question = question

    def __unicode__(self):
        from django.template import Template, Context
        template_context = get_template_context(self.form.spec, self.form.context)
        t = Template(self.question.question)
        c = Context(template_context)
        return t.render(c)

class FormBuilder(object):
    def __init__(self, spec):
        self.spec = spec
        self.klass = None

    def get_form(self, context, *args, **kwargs):
        if self.klass is None:
            self.build()

        form = self.klass(*args, **kwargs)
        form.context = context

        for question in self.spec.questions:
            form.fields[question.id].label = TextTemplate(form, question)
        return form

    def build(self):
        fields = {}
        for question in self.spec.questions:
            fields[question.id] = self.build_field(question)
        klass = type('SurveyForm', (SurveyFormBase, object), fields)
        klass.spec = self.spec
        self.klass = klass

    def build_field(self, question):
        qtype = question.type
        if qtype == 'yes-no':
            field = forms.ChoiceField(widget=forms.RadioSelect,
                                      choices=[('yes', 'Yes'),
                                               ('no', 'No')])

        elif qtype == 'options-multiple':
            field = forms.MultipleChoiceField(
                            widget=forms.CheckboxSelectMultiple,
                            choices=question.options)

        elif qtype == 'options-single':
            field = forms.ChoiceField(widget=forms.RadioSelect,
                                      choices=question.options)

        elif qtype == 'date':
            field = forms.DateField(widget=DatePickerWidget,
                                    help_text="Date format: day/month/year",
                                    input_formats=['%Y-%m-%d', '%d/%m/%Y',
                                                   '%d/%m/%y', '%d-%m-%y',
                                                   '%d-%m-%Y', '%b %d %Y',
                                                   '%b %d, %Y', '%d %b %Y',
                                                   '%d %b, %Y', '%B %d %Y',
                                                   '%B %d, %Y', '%d %B %Y',
                                                   '%d %B, %Y'])

        elif qtype == 'date-or-option':
            field = DateOrOptionField(option=question.text)

        elif qtype == 'advise':
            field = AdviseField()

        elif qtype == 'month-year':
            field = MonthYearField()

        elif qtype == 'postcode':
            field = PostCodeField()
        elif qtype.startswith('postcode-'):
            postcode, country = qtype.split('-')
            field = PostCodeField(country=country)

        elif qtype == 'table-of-selects':
            field = TableOfSelectsField(rows=question.rows,
                                        columns=question.columns,
                                        choices=question.choices,
                                        required=False)

        elif qtype == 'table-of-options-single':
            qta = question.type_args
            if (qta and isclass(qta[0]) and issubclass(qta[0], d.Question)):
                # We're dealing args derived from another question.
                args = qta + [None]
                q = args[0]
                rows = q.options
                if args[1] is not None:
                    keys = args[1]
                    rows = [(key, value) for key, value in q.options
                            if key in keys]

                def checker(rows, qid):
                    '''A closure that holds rows and question id of the field.'''
                    def _checker(data):
                        values = qid in data and data[qid]
                        if not values:
                            return []
                        values = map(int, values) # FIXME XXX
                        required = []
                        for index, pair in enumerate(rows):
                            k, v = pair
                            if k in values:
                                required.append(index)
                        return required
                    return _checker

                required_rows = checker(rows, q().id)
            elif (qta and isinstance(qta[0], str)):
                # We're dealing with literal args
                rows = zip(xrange(len(qta)), qta)
                required_rows = None
            else:
                raise NotImplementedError('Question type_args unrecognised.')

            field = TableOptionsSingleField(options=question.options,
                                            rows=rows,
                                            required_rows=required_rows)

        else:
            field = forms.CharField()

        field.required = False
        return field

class SurveyAnswerEncoder(json.JSONEncoder):
    def default(self, obj):
        import datetime
        if isinstance(obj, datetime.date):
            return obj.strftime('%d/%m/%Y')
        return super(JSONSurveyEncoder, self).default(obj)

class JavascriptBuilder(object):
    def __init__(self, spec):
        self.spec = spec

    def get_javascript(self, context):
        responses = {}
        values = context.response.values
        ids = self.spec.get_responses()
        for id in ids:
            responses[id] = values[id]

        profiles = {}
        values = context.profile.values
        ids = self.spec.get_profiles()
        for id in ids:
            profiles[id] = values[id]

        conditions = []
        for key, condition in self.spec.get_conditions().items():
            conditions.append('''"%s": %s''' % (key, condition.js))
        conditions = '{ %s }' % ', '.join(conditions)

        questions = []
        for question in self.spec.questions:
            questions.append(question.id)

        prefills = ['''{''']
        for key, prefill in self.spec.get_prefills().items():
            prefills.append('''"%s": %s,''' % (key, prefill.js))
        prefills.append('''}''')
        prefills = ''.join(prefills)

        param = {
            'modifier': json.dumps(self.spec.get_modifier()),
            'modified': json.dumps(self.spec.get_modified()),
            'profiles': json.dumps(profiles, cls=SurveyAnswerEncoder),
            'responses': json.dumps(responses, cls=SurveyAnswerEncoder),
            'prefills': prefills,
            'conditions': conditions,
            'questions': json.dumps(questions)
        }

        return '''{"modifier": %(modifier)s,
                   "modified": %(modified)s,
                   "profiles": %(profiles)s,
                   "responses": %(responses)s,
                   "prefills": %(prefills)s,
                   "questions": %(questions)s,
                   "conditions": %(conditions)s}''' % param

