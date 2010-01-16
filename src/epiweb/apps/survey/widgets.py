from django import forms

class DatePickerWidget(forms.TextInput):
    def __init__(self, attrs={}):
        forms.TextInput.__init__(self, attrs={'class': 'sDateField'})
    
