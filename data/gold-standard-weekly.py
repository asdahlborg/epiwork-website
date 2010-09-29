# Weekly evaluation of disease symptoms

class WeeklyQ1(d.Question):
  question = 'Did you have one or more of the following symptoms since your ' \
             'last visit?'
  type = 'options-multiple'
  options = ((0, 'No symptoms'),
             (1, 'Fever (i.e. high temperature) and /or chills'),
             (2, 'Watery, bloodshot eyes'),
             (3, 'Runny or blocked nose'),
             (4, 'Sneezing'),
             (5, 'Sore throat'),
             (6, 'Cough'),
             (7, 'Coloured sputum'),
             (8, 'Headache'),
             (9, 'Muscle pain'),
             (10, 'Chest pain'),
             (11, 'Feeling tired or exhausted'),
             (12, 'Loss of appetite'),
             (13, 'Nausea'),
             (14, 'Vomiting'),
             (15, 'Diarrhoea'),
             (16, 'Other'),
             )

# N.B. There is no WeeklyQ2.  Instead there is a db check.

# Check database: was the participant STILL ILL at the time of their last visit
# (i.e. they said "I am still ill" in response to Q5 below last time?)

# Yes: If the participant reported symptoms during the last visit, continue
# with Q3
# No: Then this could potentially be the start of a "new" illness, continue
# with Q4

# If the participant was STILL ILL on their last visit and has reported
# symptoms this time:
class WeeklyQ3(d.Question):
  question = 'On DATE OF LAST VISIT you reported that you were still ill ' \
             'with symptoms that began on DATE OF FIRST SYMPTOMS. Are ' \
             'the symptoms you reported today part of the same bout ' \
             'of illness?'
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'),
             )
# If NO: This means that the current symptoms are the start of a "new" illness,
# continue with Q4

# if YES: This means that the current symptoms are the continuation of the same
# bout of illness as the previous visit. The remainder of the symptoms
# questionnaire (onset date, further details about symptoms, details about
# seeking medical attention, treatment, time off work/school) can be pre-filled
# with their previous answers:

# "To save you time, we have filled in the information you gave us previously
# about your illness. Please check that it is still correct, and make any
# changes -- for instance, if you have visited a doctor since you last completed
# the survey."

class WeeklyQ4(d.Question):
  question = 'When did the first symptoms appear?'
  type = 'date'

class WeeklyQ5(d.Question):
  question = 'When did your symptoms end?'
  type = 'date'
# We also need the option of "I am still ill"

class WeeklyQ6(d.Question):
  question = 'Did you have fever ?'
  type = 'options-single'
  options = ((0, 'No'),
             (1, 'Yes'),
             (2, "I don't know"),
             )

class WeeklyQ6b(d.Question):
  question = 'If you had a fever, what was the highest temperature measured? '
  type = 'options-single'
  options = ((0, '37C - 37.5C'),
             (1, '37.5C - 38C'),
             (2, '38C - 39C'),
             (3, '39C - 40C'),
             (4, 'More than 40C'),
             (5, 'I did not measure it with a thermometer'),
             )

class WeeklyQ7(d.Question):
  question = 'Did the symptoms develop abruptly (sudden high fever ' \
             'or chills) over a couple of hours ?'
  type = 'options-single'
  options = ((0, 'No'),
             (1, 'Yes'),
             (2, "I don't know"),
             )

class WeeklyQ8(d.Question):
  question = 'Because of your symptoms, did you seek medical attention by ' \
             'visiting (seeing face to face) any of the following (tick all ' \
             'that apply)?'
  type = 'options-multiple'
  options = ((0, "General practitioner (GP) or GP's practice nurse"),
             (1, 'Hospital admission'),
             (2, 'Hospital accident & emergency department/out of hours service'),
             (3, 'Other'),
             )

# this should be asked for each option ticked in the previous question
class WeeklyQ8b(d.Question):
  question = 'How soon after your symptoms appeared did you seek medical ' \
             'attention ?'
  type = 'options-single'
  options = ((0, '<12 hours'),
             (1, '12-24 hours (1 day)'),
             (2, '2 days'),
             (3, '3 days'),
             (4, '4 days'),
             (5, '5-7 days'),
             (6, '>7 days'),
             )

class WeeklyQ8c(d.Question):
  question = 'Because of your symptoms, did you seek medical attention by ' \
             'telephone with any of the following (tick all that apply)?'
  type = 'options-multiple'
  options = ((0, 'GP - spoke to receptionist only'),
             (1, 'GP - spoke to GP/practice nurse'),
             (2, 'NHS direct or NHS24'),
             (3, 'NPFS'),
             (4, 'Other'),
             )
# Note: this is adapted to the UK situation. Other countries will need to adapt
# this question, or it might not be an essential question in other countries

class WeeklyQ9(d.Question):
  question = 'Did you take medication for these symptoms?'
  type = 'options-multiple'  # confirm this
  options = ((0, 'No medication'),
             (1, 'Pain killers or antipyretics (e.g. paracetamol, lemsip, etc)'),
             (2, 'Expectorants (cough medication)'),
             (3, 'Antivirals (Tamiflu, Relenza)'),
             (4, 'Antibiotics'),
             (5, 'Other'),
             )
# Note: this is adapted to the UK situation. Other countries will need to adapt
# the brand names of the commonly used pain killers or antipyretics

class WeeklyQ9b(d.Question):
  question = 'How long after the beginning of your symptoms did you start ' \
             'taking antiviral medication'
  type = 'options-single'
  options = ((0, 'Same day (within 24 hours)'),
             (1, '1 day later'),
             (2, '2 days later'),
             (3, '3 days later '),
             (4, '4 days later'),
             (5, '5-7 days later'),
             (6, '>7 days later'),
             )

class WeeklyQ10(d.Question):
  question = 'Did you change your daily routine because of your illness ?'
  type = 'options-single'
  options = (
    (0, 'No'),
    (1, 'Yes, but I did not take time off work/school'),
    (2, 'Yes, I took time off work/school'),
    )
  
class WeeklyQ10b(d.Question):
  question = 'How long were you off work/school ?'
  type = 'options-single'
  options = (
    (0, '1 day'),
    (1, '2 days'),
    (2, '3 days '),
    (3, '4 days'),
    (4, '5 days'),
    (5, '6 days'),
    (6, '1 to 2 weeks'),
    (7, '2 to 3 weeks'),
    (8, '>3 weeks'),
    )
  
class WeeklyQ10c(d.Question):
  question = 'Are you still off work/school ?'
  type = 'options-single'
  options = (
    (0, 'Yes'),
    (1, 'No'),
    )
  
class WeeklyQ11(d.Question):
  question = 'How many people in your household have had flu-like symptoms ' \
             'in the past week?'
  type = 'options-single'
  options = ((0, '0')
             (1, '1'),       
             (2, '2'),       
             (3, '3 '),      
             (4, '4'),       
             (5, '5'),       
             (6, '6'),
             (99, 'more than 6'),
             )

# (if no seasonal flu vaccination yet reported)
class WeeklyQ12(d.Question):
  question = 'According to our data you did not receive a seasonal flu ' \
             'vaccination?'
  type = 'options-single'
  options = (
    (0, 'Yes, I did not receive a seasonal flu vaccination'),
    (1, 'No, meanwhile I have received a seasonal flu vaccination'),
    )

class GoldStandardWeekly(d.Survey):
    id = 'gold-standard-weekly-0.1.0'
    rules = (
      WeeklyQ1,
      # { if-still-ill: WeeklyQ3 },
      # { (WeeklyQ3 'is' 0) : 'Notify user that answers are prefilled' },
      { (WeeklyQ1, 'is-not', 0):( WeeklyQ4,
                                  WeeklyQ5,
                                  WeeklyQ6,
                                  { ( WeeklyQ6, 'is', 1 ) : ( WeeklyQ6b ) },
                                  WeeklyQ7,
                                  WeeklyQ8,
                                  WeeklyQ8b, #  table dependent of WeeklyQ8
                                  WeeklyQ8c,
                                  WeeklyQ9,
                                  { (3, 'is-in', WeeklyQ9) : ( WeeklyQ9b, ) },
                                  WeeklyQ10,
                                  { (WeeklyQ10, 'is', 2) : ( WeeklyQ10b,
                                                             WeeklyQ10c ) },
                                  ) },
      WeeklyQ11,
      # WeeklyQ12, # dependent on report of seasonal flu vaccination in intake
      )
