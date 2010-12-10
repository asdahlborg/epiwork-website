class RegQ1(d.Question):
    question = 'What is your gender?'
    type = 'options-single'
    options = (
        (0, 'Male'),
        (1, 'Female'),
    )

class RegQ2(d.Question):
    question = 'What is your occupation'
    type = 'options-single'
    options = (
        (0, 'Student'),
        (1, 'Working'),
        (2, 'Stay at home/work at home'),
        (3, 'Retired'),
        (4, 'Other'),
    )

class RegQ3(d.Question):
    question = 'Which transport do you use?'
    type = 'options-single'
    options = (
        (0, 'Walking/bicycle/scooter'),
        (1, 'Public transport'),
        (2, 'Car'),
        (3, 'Carpooling'),
        (4, 'Motorbike'),
    )

class RegQ4(d.Question):
    question = 'How often a year do you have common colds or flu-like diseases?'
    type = 'options-single'
    options = (
        (0, 'Less than 2 times a year'),
        (1, 'Between 2 and 5 times a year'),
        (2, 'More than 5 times a year'),
    )

class RegQ5(d.Question):
    question = 'Did you receive a vaccination for seasonal flu (not Mexican flu) this year?'
    type = 'options-single'
    options = (
        (0, 'No'),
        (1, 'Yes'),
    )

class RegQ6(d.Question):
    question = 'Did you receive a vaccination for the Mexican flu (not seasonal flu)?'
    type = 'options-single'
    options = (
        (0, 'No'),
        (1, 'Yes'),
    )

class RegQ7(d.Question):
    question = 'Are you pregnant?'
    type = 'options-single'
    options = (
        (0, 'No'),
        (1, 'Yes'),
    )

class RegQ8(d.Question):
    question = 'Do you have one of the following disorders?'
    type = 'options-multiple'
    blank = True
    options = (
        (0, 'Asthma'),
        (1, 'Lung disorder (COPD, emphysema, ...)'),
        (2, 'Heart disorder'),
        (3, 'Kidney disorder'),
        (4, 'Diabetes'),
        (5, 'Autoimmune disease'),
        (6, 'Cancer'),
        (7, 'Immunocompromised'),
    )

class RegQ9(d.Question):
    question = 'Do you have one of the following allergies?'
    type = 'options-multiple'
    blank = True
    options = (
        (0, 'Hay fever'),
        (1, 'Food allergy (lactose intolerance, gluten, ...)'),
        (2, 'Medicine (aspirin, antibiotics)'),
        (3, 'House dust mite'),
        (4, 'Domestic animals/pets'),
    )

class RegQ10(d.Question):
    question = 'Do you follow a special diet?'
    type = 'options-single'
    options = (
        (0, 'No'),
        (1, 'Vegetarian'),
        (2, 'Veganism'),
        (3, 'Low-calorie'),
        (4, 'Other'),
    )

class RegQ11(d.Question):
    question = 'Do you smoke?'
    type = 'options-single'
    options = (
        (0, 'No'),
        (1, 'Yes, sometimes'),
        (2, 'Yes, everyday'),
    )

class RegQ12(d.Question):
    question = 'With how many people do you live at home?'
    type = 'options-single'
    options = (
        (0, 'I live alone'),
        (1, 'Together with one or more adults (18+)'),
        (2, 'Together with one or more children (18-)'),
        (3, 'Together with other adults and children'),
    )

class RegQ13(d.Question):
    question = 'Are the children going to school or day-care?'
    type = 'options-multiple'
    blank = True
    options = (
        (0, 'No, they stay at home'),
        (1, 'Yes, to school'),
        (2, 'Yes, to day-care'),
    )

class RegQ14(d.Question):
    question = 'Do you have pets at home?'
    type = 'options-multiple'
    blank = True
    options = (
        (0, 'Yes, one or more dogs'),
        (1, 'Yes, one or more cats'),
        (2, 'Yes, one or more birds'),
        (3, 'Yes, one or more other animals'),
    )

class Survey(d.Survey):
    id = 'dev-profile-0.0'
    rules = (
        RegQ1,
        RegQ2,
        RegQ3,
        RegQ4,
        RegQ5,
        RegQ6,
        d.If(d.Equal(RegQ1, 1)) (
            RegQ7,
        ),
        RegQ8,
        RegQ9,
        RegQ10,
        RegQ11,
        RegQ12,
        RegQ13,
        RegQ14,
    )

