from django import forms
from epiweb.apps.survey.data import Survey, Section, Question

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

    field.label = question.label
    field.required = False

    return field

def generate_form(section, values=None):
    if values:
        form = forms.Form(values)
    else:
        form = forms.Form()

    for question in section.questions:
        form.fields[question.id] = create_field(question)

    return form

