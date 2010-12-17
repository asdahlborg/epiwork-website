# Weekly evaluation of disease symptoms including contact questions.

class WeeklyQ1(d.Question):
  question = """Did you have one or more of the following symptoms
  {% if LAST_SURVEY %}since your last visit{% else %}during the last
  week{% endif %}? (Tick all that apply)"""
  type = 'options-multiple'
  options = ((1, 'Fever'),
             (17, 'Chills'),
             (3, 'Runny or blocked nose'),
             (4, 'Sneezing'),
             (5, 'Sore throat'),
             (6, 'Cough'),
             (18, 'Shortness of breath'),
             (8, 'Headache'),
             (9, 'Muscle pain'),
             (10, 'Chest pain'),
             (11, 'Feeling tired or exhausted'),
             (12, 'Loss of appetite'),
             (7, 'Coloured sputum'),
             (2, 'Watery, bloodshot eyes'),
             (13, 'Nausea'),
             (14, 'Vomiting'),
             (15, 'Diarrhoea'),
             (19, 'Stomach ache'),
             (16, 'Other'),
             (0, 'No symptoms'),
             )

class WeeklyQ1b(d.Question):
  question = 'Did your symptoms develop suddenly?'
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'),
             (2, "I don't know"), )

class WeeklyQ2(d.Question):
  question = 'Did you take your temperature?'
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'),
             (2, "I don't know"), )

class WeeklyQ2b(d.Question):
  question = """When you measured your temperature, what was the highest
  temperature measured?"""
  type = 'options-single'
  options = ((0, 'Below 37C'),
             (1, '37 - 37.4C'),
             (2, '37.5 - 37.9C'),
             (3, '38 - 38.9C'),
             (4, '39 - 39.9C'),
             (5, '40C or more'), )

class WeeklyQ2c(d.Question):
  question = 'When did the fever start?' 
  type = 'date'
  # or "I don't remember"

class WeeklyQ3(d.Question):
  question = """On {{ LAST_SURVEY.DATE|date:'l F jS' }} you reported that you
  were still ill with symptoms that began on
  {{ LAST_SURVEY.WeeklyQ4|date:'l F jS' }}. Are the symptoms you reported today
  part of the same bout of illness?"""
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'), )
  
class Message1(d.Question):
  question = """To save you time, we have filled in the information you gave us
  previously about your illness. Please check that it is still correct, and
  make any changes -- for instance, if you have visited a doctor since you last
  completed the survey."""
  type = 'advise'
  
class WeeklyQ4(d.Question):
  question = 'When did the first symptoms appear?'
  type = 'date'

class WeeklyQ5(d.Question):
  question = 'When did your symptoms end?'
  type = 'date-or-option'
  text = 'I am still ill'

class WeeklyQ6(d.Question):
  question = """Because of your symptoms, did you seek medical attention by
  visiting (seeing face to face) any of the following (tick all that apply)?"""
  type = 'options-multiple'
  options = ((0, "Yes: family doctor or family doctor's practice nurse"),
             (1, 'Yes: Hospital admission'),
             (2, """Yes: Hospital accident & emergency department/out of hours
             service"""),
             (3, 'Yes: Other'),
             (4, 'No'),
             (5, 'No, but I have an appointment scheduled in the future'), )

# this should be asked for each option ticked in the previous question
class WeeklyQ6b(d.Question):
  question = """How soon after your symptoms appeared did you seek medical
  attention?"""
  type = 'table-of-options-single'
  type_args = [WeeklyQ6, [0,1,2,3]]
  options = ((0, '<12 hours'),
             (1, '12-24 hours (1 day)'),
             (2, '2 days'),
             (3, '3 days'),
             (4, '4 days'),
             (5, '5-7 days'),
             (6, '>7 days'), )

class WeeklyQ6c(d.Question):
  question = """Because of your symptoms, did you seek medical attention by
  telephone with any of the following (tick all that apply)?"""
  type = 'options-multiple'
  options = ((0, 'Yes: Family doctor - spoke to receptionist only'),
             (1, 'Yes: Family doctor - spoke to doctor or nurse'),
             (2, 'Yes: National health advice service'),
             (3, 'Yes: National pandemic flu service'),
             (4, 'Yes: Other'),
             (5, 'No'),)

class WeeklyQ7(d.Question):
  question = "Did you take medication for these symptoms?"
  type = 'options-multiple'
  options = ((0, "No medication"),
             (1, """Pain killers or antipyretics (e.g. paracetamol, lemsip,
             ibuprofen, aspirin, etc)"""),
             (2, "Expectorants (cough medicine)"),
             (3, "Antivirals (Tamiflu, Relenza)"),
             (4, "Antibiotics"),
             (5, "Other"), )

class WeeklyQ7b(d.Question):
  question = """How long after the beginning of your symptoms did you start
  taking antiviral medication?"""
  type = 'options-single'
  options = ((0, "Same day (within 24 hours)"),
             (1, "1 day later"),
             (2, "2 days later"),
             (3, "3 days later "),
             (4, "4 days later"),
             (5, "5-7 days later"),
             (6, ">7 days later"), )

class WeeklyQ8(d.Question):
  question = "Did you change your daily routine because of your illness?"
  type = 'options-single'
  options = ((0, "No"),
             (1, "Yes, but I did not take time off work/school"),
             (2, "Yes, I took time off work/school"), )

class WeeklyQ8b(d.Question):
  question = "Are you still off work/school?"
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'), )

class WeeklyQ8c(d.Question):
  question = "How long were you off work/school?"
  type = 'options-single'
  options = ((0, "1 day"),
             (1, "2 days"),
             (2, "3 days"),
             (3, "4 days"),
             (4, "5 days"),
             (5, "6 days"),
             (6, "1 to 2 weeks"),
             (7, "2 to 3 weeks"),
             (8, ">3 weeks"), )

class WeeklyQ9a(d.Question):
  question = """How many people did you meet inside or outside your household
  that had flu-like symptoms in the past week?

  <em>Inside</em> your household:"""  # Emphasise the word 'Inside' 
  type = 'options-single'
  options = ((0, "0"),
             (1, "1"),
             (2, "2"),
             (3, "3"),
             (4, "4"),
             (5, "5"),
             (6, ">5"),
             (7, "Don't know"), )

class WeeklyQ9b(d.Question):
  question = """How many people did you meet inside or outside your household
  that had flu-like symptoms in the past week?

  <em>Outside</em> your household:"""  # Emphasise the word 'Outside' 
  type = 'options-single'
  options = ((0, "0"),
             (1, "1"),
             (2, "2"),
             (3, "3"),
             (4, "4"),
             (5, "5"),
             (6, ">5"),
             (7, "Don't know"), )

class WeeklyQ10(d.Question):
  question = """According to our data you did not receive a seasonal flu
  vaccination. Have you had one in the meantime?"""
  type = 'options-single'
  options = ((0, 'Meanwhile I have received a seasonal flu vaccination'),
             (1, 'I did not receive a seasonal flu vaccination'), )

class WeeklyQ11(d.Question):
  question = 'What do you think yourself is causing your symptoms?'
  type = 'options-single'
  options = ((0, "Influenza or influenza-like illness"),
             (1, "Common cold"),
             (2, "Allergy/hay fever"),
             (3, "Gastroenteritis/gastric flu"),
             (4, "I don't have an idea"), )

class ContactQ1(d.Question):
  question = """How many people did you have conversational contact with
             yesterday?"""
  type = 'table-of-selects'
  rows = ['Home', 'Work', 'Other']
  columns = ['0-4 years',
             '5-18 years',
             '19-44 years',
             '45-64 years',
             '65+ years',]
  choices = (( 0,  '0'),
             ( 1,  '1'),
             ( 2,  '2'),
             ( 3,  '3'),
             ( 4,  '4'),
             ( 5,  '5'),
             ( 6,  '6'),
             ( 7,  '7'),
             ( 8,  '8'),
             ( 9,  '9'),
             (10, '>9'),)

class ContactQ2(d.Question):
  question = 'How many people did you have physical contact with yesterday?'
  type = 'table-of-selects'
  rows = ['Home', 'Work', 'Other']
  columns = ['0-4 years',
             '5-18 years',
             '19-44 years',
             '45-64 years',
             '65+ years',]
  choices = (( 0,  '0'),
             ( 1,  '1'),
             ( 2,  '2'),
             ( 3,  '3'),
             ( 4,  '4'),
             ( 5,  '5'),
             ( 6,  '6'),
             ( 7,  '7'),
             ( 8,  '8'),
             ( 9,  '9'),
             (10, '>9'),)

class ContactQ3(d.Question):
  question = """On a normal day, how much time do you spend on public
  transport (bus, train, undergound)?"""
  type = 'options-single'
  options = ((0, 'No time at all'),
             (1, '0-30 minutes'),
             (2, '30 minutes – 1,5 hours'),
             (3, '1,5 hours – 4 hours'),
             (4, '>4 hours'), )

class ContactQ4(d.Question):
  question = """Not including public transport, how long did you spend in an
  enclosed indoor space (e.g. office, classroom, bar, cinema) with more than 10
  other people yesterday ?"""
  type = 'options-single'
  options = ((0, 'No time at all'),
             (1, '0-30 minutes'),
             (2, '30 minutes – 1,5 hours'),
             (3, '1,5 hours – 4 hours'),
             (4, '>4 hours'),)
  
class Survey(d.Survey):
  id = 'gold-standard-weekly-with-contact-1.6'

  # Propositions depending on the previous response.
  
  # WeeklyQ11 requires an answer so if its value is empty in the previous
  # response then the previous response must not exist.
  previous_response_exists = ~ d.Empty(d.Response('WeeklyQ11'))
  previously_still_ill = previous_response_exists & \
                         d.Equal(d.Response('WeeklyQ5'), 0)

  # Propositions depending on (previous) answers in this response.
  symptoms_present             = ~ d.In(WeeklyQ1, [0]) & \
                                 d.In(WeeklyQ1, [1,2,3,4,5,6,7,8,9,10,11,
                                                 12,13,14,15,16,17,18,19])
  took_temp                    = d.Equal(WeeklyQ2, 0)
  fever_among_symptoms         = d.In(WeeklyQ1, [1])
  temp_over_37half             = d.In(WeeklyQ2b, [2,3,4,5])
  took_antivirals              = d.In(WeeklyQ7, [3])
  reported_no_seasonal_flu_jab = ~ d.Equal(d.Profile('IntakeQ9'), 0)
  still_ill                    = d.Equal(WeeklyQ3, 0)
  sought_medical_attention     = d.In(WeeklyQ6, [0,1,2,3])
  
  rules = ( WeeklyQ1,
            d.If(symptoms_present) (WeeklyQ1b, WeeklyQ2),
            d.If(symptoms_present & took_temp) (WeeklyQ2b),
            d.If(fever_among_symptoms | (took_temp & temp_over_37half))
            (WeeklyQ2c),
            d.If(previously_still_ill & symptoms_present) (WeeklyQ3),
            d.If(still_ill) (Message1),
            d.If(symptoms_present)
            ( WeeklyQ4,
              WeeklyQ5,
              WeeklyQ6,
              d.If(sought_medical_attention) (WeeklyQ6b),
              WeeklyQ6c,
              WeeklyQ7,
              d.If(took_antivirals) (WeeklyQ7b),
              WeeklyQ8,
              d.If(d.Equal(WeeklyQ8, 2)) (WeeklyQ8b, WeeklyQ8c,)),
            WeeklyQ9a,
            WeeklyQ9b,
            d.If(reported_no_seasonal_flu_jab) (WeeklyQ10),
            # TODO Possibly update IntakeQ9 here?
            d.If(symptoms_present) (WeeklyQ11),

            ContactQ1,
            ContactQ2,
            ContactQ3,
            ContactQ4,
            )

  # TODO tidy up this syntax: see survey.py lines 100-125
  prefill = { WeeklyQ4:  still_ill,
              WeeklyQ5:  still_ill,
              WeeklyQ6:  still_ill,
              WeeklyQ6b: still_ill,
              WeeklyQ6c: still_ill,
              WeeklyQ7:  still_ill,
              WeeklyQ7b: still_ill,
              WeeklyQ8:  still_ill,
              WeeklyQ8b: still_ill,
              WeeklyQ8c: still_ill,
              WeeklyQ9a: still_ill,
              WeeklyQ9b: still_ill,
              }

