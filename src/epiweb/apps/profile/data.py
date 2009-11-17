from epiweb.apps.survey import definition as d

_ = lambda x: x

class RegQ1(d.Question):
    question = _('What is your gender?')
    type = 'options-single'
    options = ('Male', 'Female')

class RegQ2(d.Question):
    question = _('What is your occupation')
    type = 'options-single'
    options = (
        'Student',
        'Working',
        'Stay at home/work at home',
        'Retired',
        'Other'
    )

class RegQ3(d.Question):
    question = _('Which transport do you use?')
    type = 'options-single'
    options = (
        'Walking/bicycle/scooter',
        'Public transport',
        'Car',
        'Carpooling',
        'Motorbike'
    )

class RegQ4(d.Question):
    question = _('How often a year do you have common colds or flu-like diseases?')
    type = 'options-single'
    options = (
        'Less than 2 times a year',
        'Between 2 and 5 times a year',
        'More than 5 times a year'
    )

class RegQ5(d.Question):
    question = _('Did you receive a vaccination for seasonal flu (not Mexican flu) this year?')
    type = 'options-single'
    options = ('No', 'Yes')

class RegQ6(d.Question):
    question = _('Did you receive a vaccination for the Mexican flu (not seasonal flu)?')
    type = 'options-single'
    options = ('No', 'Yes')

class RegQ7(d.Question):
    question = _('Are you pregnant?')
    type = 'options-single'
    options = ('No', 'Yes')

class RegQ8(d.Question):
    question = _('Do you have one of the following disorders?')
    type = 'options-multiple'
    options = (
        _('Asthma'),
        _('Lung disorder (COPD, emphysema, ...)'),
        _('Heart disorder'),
        _('Kidney disorder'),
        _('Diabetes'),
        _('Autoimmune disease'),
        _('Cancer'),
        _('Immunocompromised'),
    )

class RegQ9(d.Question):
    question = _('Do you have one of the following allergies?')
    type = 'options-multiple'
    options = (
        _('Hay fever'),
        _('Food allergy (lactose intolerance, gluten, ...)'),
        _('Medicine (aspirin, antibiotics)'),
        _('House dust mite'),
        _('Domestic animals/pets'),
    )

class RegQ10(d.Question):
    question = _('Do you follow a special diet?')
    type = 'options-single'
    options = (
        _('No'),
        _('Vegetarian'),
        _('Veganism'),
        _('Low‐calorie'),
        _('Other'),
    )

class RegQ11(d.Question):
    question = _('Do you smoke?')
    type = 'options-single'
    options = (
        _('No'),
        _('Yes, sometimes'),
        _('Yes, everyday')
    )

class RegQ12(d.Question):
    question = _('With how many people do you live at home?')
    type = 'options-single'
    options = (
        _('I live alone'),
        _('Together with one or more adults (18+)'),
        _('Together with one or more children (18‐)'),
        _('Together with other adults and children'),
    )

class RegQ13(d.Question):
    question = _('Are the children going to school or day-care?')
    type = 'options-multiple'
    options = (
        _('No, they stay at home'),
        _('Yes, to school'),
        _('Yes, to day‐care'),
    )

class RegQ14(d.Question):
    question = _('Do you have pets at home?')
    type = 'options-multiple')
    options = (
        _('Yes, one or more dogs'),
        _('Yes, one or more cats'),
        _('Yes, one or more birds'),
        _('Yes, one or more other animals'),
    )

class UserProfile(d.Survey):
    rules = (
        ReqQ01,
        ReqQ02,
        ReqQ03,
        ReqQ04,
        ReqQ05,
        ReqQ06,
        { (Reg01, 'is', 1) : (
            ReqQ07,
        ) },
        ReqQ08,
        ReqQ09,
        ReqQ10,
        ReqQ11,
        ReqQ12,
        ReqQ13,
        ReqQ14,
    )

