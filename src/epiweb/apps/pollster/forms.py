from django import forms

class SurveyXmlForm(forms.Form):
    surveyxml = forms.CharField(required=True)
