import urllib2
import errno
import socket

from django import forms
from django.forms.util import ErrorList
from django.contrib.admin import widgets

from epiweb.apps.survey import definitions as d
from epiweb.apps.survey import models
from epiweb.apps.survey import widgets
from epiweb.apps.survey import parser
from epiweb.apps.survey import signals

from django.conf import settings
from epidb_client import EpiDBClient

from datetime import datetime

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import simplejson as json
except ImportError:
    import json

_ = lambda x: x

_survey_form_helper = {}
_survey_object = {}
_profile_object = None

class UsingInvalidDataError(Exception):
    pass

class UnknownSurveyError(Exception):
    def __init__(self, survey_id):
        self.survey_id = survey_id
        msg = 'Unknown survey id: %s' % self.survey_id
        Exception.__init__(self, msg)

_survey = {}
_profile = {}
_survey_object = {}
_form = {}

def get_survey(survey_id=None):
    if survey_id is None:
        survey_id = settings.SURVEY_ID

    survey = _survey.get(survey_id, None)
    if survey is None:
        survey = _get_survey_object(survey_id)

        global _survey
        _survey[survey_id] = survey

    return survey

def get_profile(profile_survey_id=None):
    if profile_survey_id is None:
        profile_survey_id = settings.SURVEY_PROFILE_ID

    profile = _profile.get(profile_survey_id, None)
    if profile is None:
        profile = _get_survey_object(profile_survey_id)

        global _profile
        _profile[profile_survey_id] = profile

    return profile

def _get_survey_object(survey_id):
    global _survey_object
    object = _survey_object.get(survey_id, None)
    if object is None:
        try:
            data = models.Survey.objects.get(survey_id=survey_id)
        except models.Survey.DoesNotExist:
            raise UnknownSurveyError(survey_id)
        object = _parse_survey_specification(data.specification)
        object._data = data
        _survey_object[survey_id] = object
    return object

def _parse_survey_specification(specification):
    return parser.parse(specification)

def get_form_class(survey_id):
    global _form
    form = _form.get(survey_id, None)
    if form is None:
        object = _get_survey_object(survey_id)
        form = _generate_form_class(object)
        _form[survey_id] = form
    return form

def _generate_form_class(survey):
    helper = SurveyFormHelper(survey)
    return helper.create_form

def get_global_id(user):
    try:
        user2 = models.SurveyUser.objects.get(user=user)
        return user2.global_id
    except models.SurveyUser.DoesNotExist:
        return None

class JavascriptHelper:
    def __init__(self, survey, survey_user, container_id='survey',
                 question_id_prefix="q_"):
        self.survey = survey
        self.survey_user = survey_user
        self.container = container_id
        self.prefix = question_id_prefix
        self.js = None
        self.checked_profiles = []

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
        lines += self._create_profile_data()
        lines.append("s.init();")
        lines.append("})('%s', '%s');" % (self.container, self.prefix))
        self.js = "\n".join(lines)

    def _create_question_list(self):
        return ["s.qids = [%s];" % ", ".join(map(lambda x: "'%s'" % x.id, 
                                                 self.survey.questions))]

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
                lines.append("s.affected['%s'] = new Array(%s);" % \
                    (question.id, ', '.join(map(lambda x: "'%s'" % x.id, 
                                            self.survey.affected[question]))))
        return lines
        
    def _create_rules(self):
        lines = []
        lines.append("s.rule = {};")

        for question in self.survey.questions:
            rule = self._create_rule(self.survey.conditions[question])
            if rule == '':
                rule = 'true'
            lines.append("s.rule['%s'] = function() { return %s; };" % \
                         (question.id, rule))

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
                if value not in self.checked_profiles:
                    self.checked_profiles.append(value)
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

    def _create_profile_data(self):
        if len(self.checked_profiles) == 0:
            return []

        lines = []
        lines.append('s.profiles = [];')

        data = get_user_profile(self.survey_user)
        for profile in self.checked_profiles:
            name = profile.name
            value = data.get(name, 'undefined')
            tvalue = type(value).__name__
            if tvalue == 'string':
                value = "'%s'" % value
            lines.append("s.profiles['%s'] = %s;" % (name, value))

        return lines

class SurveyFormBase(forms.Form):
    def __init__(self, *args, **kwargs):
        self._survey = kwargs['survey']
        self._user = kwargs['user']
        self._profile = None
        del kwargs['survey']
        del kwargs['user']
        super(SurveyFormBase, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data

        for question in self._survey.questions:
            try:
                visible = self._evaluate_question_condition(question)
                if not visible:
                    # Question is disabled, then delete the answer
                    cleaned_data[question.id] = None
                    if question.id in self._errors.keys():
                        del self._errors[question.id]
                elif question.id in cleaned_data.keys():
                    # Answer is present
                    value = self._get_question_value(question)
                    if len(value) == 0 and not question.blank:
                        # Answer is blank but the question need
                        # to be answered
                        msg = _(u'Please answer this question.')
                        self._errors[question.id] = ErrorList([msg])
                        del cleaned_data[question.id]
                        
            except UsingInvalidDataError:
                msg = _(u'Please correct the previous answers.')
                self._errors[question.id] = ErrorList([msg])
                del cleaned_data[question.id]
                
        return cleaned_data

    def _evaluate_question_condition(self, question):
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
        if self._profile is None:
            self._profile = get_user_profile(self._user)

        value = self._profile.get(name, None)
        tvalue = type(value).__name__
        if value is None:
            return None
        else:
            return [value]

    def _get_question_value(self, question):
        if question.id not in self.cleaned_data.keys():
            raise UsingInvalidDataError()
        res = self.cleaned_data.get(question.id, None)
        if res == None:
            res = []
        elif question.type in ['options-single']:
            res = res.strip()
            if res == '':
                res = []
            else:
                res = [int(res)]
        elif question.type in ['options-multiple']:
            res = map(lambda x: int(x), res)
        else:
            res = [res]

        return res

    def _get_value(self, value):
        t = type(value).__name__    
        if t == 'tuple':
            return self._evaluate(value)
        elif t == 'instance':
            if isinstance(value, d.Question):
                return self._get_question_value(value)
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

    def create_form(self, survey_user, data=None):
        if self.form_class is None:
            self._generate_form()

        if data is None:
            return self.form_class(survey=self.survey, user=survey_user)
        else:
            return self.form_class(data, survey=self.survey, user=survey_user)

    def _generate_form(self):
        fields = {}
        for question in self.survey.questions:
            fields[question.id] = self._create_field(question)
        self.form_class = type('SurveyForm', (SurveyFormBase, object), fields)

    def _create_field(self, question):
        # TODO: add more data type
        if question.type == 'yes-no':
            field = forms.ChoiceField(widget=forms.RadioSelect,
                                      choices=[('yes', _('Yes')), 
                                               ('no', _('No'))])
    
        elif question.type == 'options-multiple':
            field = forms.MultipleChoiceField(
                        widget=forms.CheckboxSelectMultiple,
                        choices=question.options)
    
        elif question.type == 'options-single':
            field = forms.ChoiceField(widget=forms.RadioSelect,
                                      choices=question.options)
    
        elif question.type == 'date':
            field = forms.DateField(widget=widgets.DatePickerWidget,
                                    help_text="Date format: day/month/year",
                                    input_formats=['%Y-%m-%d', '%d/%m/%Y', 
                                                   '%d/%m/%y', '%d-%m-%y', 
                                                   '%d-%m-%Y', '%b %d %Y',
                                                   '%b %d, %Y', '%d %b %Y',
                                                   '%d %b, %Y', '%B %d %Y',
                                                   '%B %d, %Y', '%d %B %Y',
                                                   '%d %B, %Y'])
    
        else:
            field = forms.CharField()
    
        field.label = question.question
        field.required = False
    
        return field

def _format_data(type, data):
    if data is None:
        return data

    # TODO: complete this: text, options-single, options-multiple
    if type == 'date':
        data = data.strftime("%Y-%m-%d")
    return data

def _create_answers(survey, cleaned_data):
    data = {}

    for question in survey.questions:
        if not question.private:
            data[question.id] = _format_data(question.type, 
                                             cleaned_data[question.id])

    return data

def add_survey_participation(survey_user, survey_data, id=None):
    participation = models.Participation()
    participation.user = survey_user
    participation.survey = survey_data
    participation.epidb_id = id
    participation.previous_participation = survey_user.last_participation
    participation.previous_participation_date = survey_user.last_participation_date
    participation.save()

    survey_user.last_participation = participation
    survey_user.last_participation_date = participation.date
    survey_user.save()

    return participation

def add_response_queue(participation, survey, cleaned_data):
    user_id = participation.user.global_id
    survey_id = survey.id
    answers = pickle.dumps(_create_answers(survey, cleaned_data))

    queue = models.ResponseSendQueue()
    queue.participation = participation
    queue.date = datetime.utcnow()
    queue.user_id = user_id
    queue.survey_id = survey_id
    queue.answers = answers
    queue.save()

    signals.response_submit.send(sender=queue,
                                 user=participation.user,
                                 date=queue.date,
                                 user_id=user_id,
                                 survey_id=survey_id,
                                 answers=answers)

def add_profile_queue(survey_user, survey, cleaned_data):
    user_id = survey_user.global_id
    profile_survey_id = survey.id
    answers = pickle.dumps(_create_answers(survey, cleaned_data))

    queue = models.ProfileSendQueue()
    queue.owner = survey_user
    queue.date = datetime.utcnow()
    queue.user_id = user_id
    queue.survey_id = profile_survey_id
    queue.answers = answers
    queue.save()

    signals.profile_update.send(sender=queue,
                                user=survey_user,
                                date=queue.date,
                                user_id=user_id,
                                survey_id=profile_survey_id,
                                answers=answers)

def get_user_profile(survey_user):
    try:
        profile = models.Profile.objects.get(user=survey_user)
        if not profile.valid:
            return None
        return pickle.loads(str(profile.data))
    except models.Profile.DoesNotExist:
        return None

def format_profile_data(profile, data):
    res = {}
    for question in profile.questions:
        value = data.get(question.id, None)
        if value is not None:
            if question.type in ['options-single']:
                value = value.strip()
                if value == '':
                    value = None
                else:
                    value = int(value)
            elif question.type in ['options-multiple']:
                value = map(lambda x: int(x), value)

        res[question.id] = value

    return res

def save_profile(survey_user, survey_data, data):
    try:
        profile = models.Profile.objects.get(user=survey_user)
    except models.Profile.DoesNotExist:
        profile = models.Profile()
        profile.user = survey_user

    profile.data = pickle.dumps(data)
    profile.survey = survey_data
    profile.valid = True
    profile.save()

