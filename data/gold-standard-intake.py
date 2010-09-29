# 'Gold Standard' Questionnaires (Deliverable of Task 2) KULeuven
# 1) New user registration: intake questions

class IntakeQ1(d.Question):
  question = 'What is your gender?'
  type = 'options-single'
  options = ((0, 'Male'),
             (1, 'Female'),
             )
  
class IntakeQ2(d.Question):
  question = 'What is your age?'
  type = 'options-single'
  options = ((0, 'Less than 1 year'),
             (1, '1 year'),
             (2, '2 years'),
             (3, '...'),
             )

# class IntakeQ3(d.Question):
#   question = 'What is your home postal code?'
#   type = 'text-input-box'
# 
# class IntakeQ4(d.Question):
#   question = 'What is your school/workplace postal code?'
#   type = 'text-input-box'

class IntakeQ5(d.Question):
  question = 'In your daily life, do you come into frequent contact with any ' \
             'of the following? (Tick all that apply)'
  type = 'options-multiple'
  options = ((0, 'Groups of children'),
             (1, 'Groups of the elderly (>65 years of age)'),
             (2, 'Patients'),
             (3, 'Large numbers of people (>10 individuals)'),
             )

# class IntakeQ6(d.Question):
#   question = 'Not counting you, how many people in each of the following age ' \
#              'groups live in your household?'
#   options = (
#     (0, '0-4'),
#     (1, '5-18'),
#     (2, '19-44'),
#     (3, '45-64'),
#     (4, '65+'),
# # Drop down menu
# 
# class IntakeQ6b(d.Question):
#   question = 'How many of ther children aged 0-4 in your household go to ' \
#              'school or day-care ?'
#   options = (
#     (, 'X'),
#     )
  
class IntakeQ7(d.Question):
  question = 'What is your daily main means of transportation?'
  type = 'options-single'
  options = ((0, 'Walking'),
             (1, 'Bike'),
             (2, 'Motorbike/scooter'),
             (3, 'Car'),
             (4, 'Public transportation (Bus, train, ...'),
             (5, 'Other'),
             )

class IntakeQ7b(d.Question):
  question = 'On a normal day, how much time do you spend on public transport' \
             ' (bus, train, underground)?'
  type = 'options-single'
  options = ((0, 'No time at all'),
             (1, '0-30 minutes'),
             (2, '30 minutes - 1,5 hours'),
             (4, '1,5 hours - 4 hours'),
             (5, '>4 hours'),
             )

# (not a core question)
class IntakeQ8(d.Question):
  question = 'How often a year do you have common colds or flu-like diseases?'
  type = 'options-single'
  options = ((0, 'Never'),
             (1, 'One or two times a year'),
             (2, 'Between 3 and 5 times a year'),
             (3, 'Between 6 and 10 times a year'),
             (4, 'More than 10 times a year'),
             )
  
class IntakeQ9(d.Question):
  question = 'Did you receive vaccination(s) for pandemic A/H1N1 Mexican flu ' \
             'during the fall or winter season 2009-2010?'
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'),
             (2, "I don't know"),
             )

class IntakeQ9b(d.Question):
  question = 'When did you receive vaccination(s) for pandemic A/H1N1 Mexican ' \
             'flu  during the fall or winter season 2009-2010 ?'
  type = 'date'
  # 'If you received two doses: date of the second dose ? XX/XX/XXXX'),
  
class IntakeQ10(d.Question):
  question = 'Did you receive vaccination(s) for seasonal flu during the fall ' \
             'or winter season 2009-2010?'
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'),
             (2, "I don't know"),
             )

class IntakeQ11(d.Question):
  question = 'Did you already  receive a seasonal flu vaccination this fall ' \
             'or winter season (2010-2011) ?'
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'),
             (2, "I don't know"),
             )
  
class IntakeQ11b(d.Question):
  question = 'When did you receive a seasonal influenza vaccination this fall ' \
             'or winter season (2010-2011) ?'
  type = 'date'
  
class IntakeQ11c(d.Question):
  question = 'What were your reasons for getting a seasonal influenza ' \
             'vaccination this fall or winter season (2010-2011) ? (Tick all ' \
             'that apply)'
  type = 'options-multiple'
  options = ((0, 'Because I belong to a risk group'),
             (1, 'Because vaccination decreases the risk of developing ' \
                 'influenza yourself'),
             (2, 'Because vaccination decreases the risk of spreading ' \
                 'influenza to others'),
             (3, 'Because my general practitioner recommended influenza ' \
                 'vaccination'),
             (4, 'Because it was recommended in my workplace/school'),
             (5, 'Because the vaccine was readily available and vaccine ' \
                 'administration was convenient'),
             (6, 'Because the vaccine was free (no cost)'),
             (7, "Because I don't want to miss work/school"),
             (8, 'Because I believe that the vaccine is effective'),
             (9, 'Other reason(s)'),
             )
  
# Note: this list is, as suggested by John Edmunds, adapted from the article by
# Hollmeyer et al., 2009 (Influenza vaccination of health care workers in
# hospitals: a review of studies on attitudes and predictors)

class IntakeQ11d(d.Question):
  question = 'What were your reasons for NOT getting a seasonal influenza ' \
             'vaccination this fall or winter season (2010-2011) ? (Tick all ' \
             'that apply)'
  type = 'options-multiple'
  options = ((0, 'Because I personally do not need influenza vaccination since' \
                 ' I do not belong to a risk group'),
             (1, 'Because it is better to build your own natural immunity ' \
              'against the flu'),
             (2, 'Because I doubt that the influenza vaccine is effective'),
             (3, 'Because I think that influenza is a minor illness'),
             (4, 'Because I am convinced that the influenza vaccine can cause' \
                 ' influenza'),
             (5, 'Because I am worried that the vaccine is not safe or will ' \
                 'cause illness or other adverse events'),
             (6, 'Because the vaccine is not readily available to me'),
             (7, 'Because the vaccine is not free of charge'),
             (8, 'Because I dislike injections'),
             (9, 'Other reason(s)'),
             )
# Note: this list is, as suggested by John Edmunds, adapted from the article by
# Hollmeyer et al., 2009 (Influenza vaccination of health care workers in
# hospitals: a review of studies on attitudes and predictors)

class IntakeQ12(d.Question):
  question = 'Do you take medication for any of the following medical' \
             ' conditions?'
  type = 'options-multiple'
  options = ((0, 'Asthma'),
             (1, 'Diabetes'),
             (2, 'Lung disorder (COPD, emphysema, ...)'),
             (3, 'Heart disorder'),
             (4, 'Kidney disorder'),
             (5, 'Immunocompromised (e.g. splenectomy, cancer treatment)'),
             )
  
class IntakeQ13(d.Question):
  question = 'Are you currently pregnant ?'
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'),
             (2, "I don't know"),
             )

class IntakeQ13b(d.Question):
  question = 'If you are currently pregnant, in which trimester of the ' \
             'pregnancy are you'
  type = 'options-single'
  options = ((0, 'First trimester (week 1-12)'),
             (1, 'Second trimester (week 13-28)'),
             (2, 'Third trimester (week 29-delivery)'),
             (3, "I don't know"),
             )

class IntakeQ14(d.Question):
  question = 'Do you smoke daily?'
  type = 'options-single'
  options = ((0, 'No'),
             (1, 'Yes, less than 10 cigarettes a day'),
             (2, 'Yes, more than 10 cigarettes a day'),
             (3, "I don't know"),
             )
  
class IntakeQ15(d.Question):
  question = 'Do you have one of the following allergies that can cause ' \
             'respiratory symptoms? (Multiple answers possible)'
  type = 'options-multiple'
  options = ((0, 'Pollen (hay fever)'),
             (1, 'House dust mite'),
             (2, 'Domestic animals/pets'),
             (3, 'Other allergies that cause respiratory symptoms (e.g.' \
                 ' sneezing, runny eyes)'),
             )

# (not a core question)  
class IntakeQ16(d.Question):
  question = 'Do you follow a special diet?'
  type = 'options-single'
  options = ((0, 'No special diet'),
             (1, 'Vegetarian'),
             (2, 'Veganism'),
             (3, 'Low-calorie'),
             (4, 'Other'),
             )
  
# (not a core question)
class IntakeQ17(d.Question):
  question = 'Do you have pets at home? (Multiple answers possible)'
  type = 'options-multiple'
  options = ((0, 'No'),
             (1, 'Yes, one or more dogs'),
             (2, 'Yes, one or more cats'),
             (3, 'Yes, one or more birds'),
             (4, 'Yes, one ore more other animals'),
             )

class Survey(d.Survey):
    id = 'gold-standard-intake-0.1.0'
    rules = ( IntakeQ1,
              IntakeQ2,
              # IntakeQ3,
              # IntakeQ4,
              IntakeQ5,
              # IntakeQ6,
              # {(IntakeQ6[0], 'is-not', 0) : ( IntakeQ6b, )},
              IntakeQ7,
              IntakeQ8,
              IntakeQ9,
              {(IntakeQ9, 'is', 0) : ( IntakeQ9b, )},
              IntakeQ10,
              IntakeQ11,
              {(IntakeQ11, 'is', 0) : ( IntakeQ11b, IntakeQ11c, )}, 
              {(IntakeQ11, 'is', 1) : ( IntakeQ11d, )}, 
              IntakeQ12,
              IntakeQ13,
              {(IntakeQ13, 'is', 0) : ( IntakeQ13b, )}, 
              IntakeQ14,
              IntakeQ15,
              IntakeQ16,
              IntakeQ17,
              )
