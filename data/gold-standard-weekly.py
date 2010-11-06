# Weekly evaluation of disease symptoms

class WeeklyQ1(d.Question):
  question = """Did you have one or more of the following symptoms since your
  last visit? (Tick all that apply)"""
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
             # (0, 'No symptoms'), # Removed to use d.Empty
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
  options = ((0, 'Below 37°C'),
             (1, '37° - 37.4°C'),
             (2, '37.5° - 37.9°C'),
             (3, '38° – 38.9°C'),
             (4, '39° - 39.9°C'),
             (5, '40°C or more'), )

class WeeklyQ2c(d.Question):
  question = 'When did the fever start?' 
  type = 'date'
  # or "I don’t remember"

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
  type = 'date'
# We also need the option of "I am still ill"

class WeeklyQ6(d.Question):
  question = """Because of your symptoms, did you seek medical attention by
  visiting (seeing face to face) any of the following (tick all that apply)?"""
  type = 'options-single'
  options = ((0, 'Yes: general practitioner (GP) or GP’s practice nurse'),
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
  options = ((0, '<12 hours'),
             (1, '12-24 hours (1 day)'),
             (2, '2 days'),
             (3, '3 days'),
             (4, '4 days'),
             (5, '5-7 days'),
             (6, '>7 days'), )

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
  type = 'options-multiple'
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
             (1, 'No'),
             (2, "I don't know"), )

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
             (7, "Don’t know"), )

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
             (7, "Don’t know"), )

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
             (4, "I don’t have an idea"), )

class Survey(d.Survey):
  id = 'gold-standard-weekly-0.1.0'
  rules = (
    WeeklyQ11,
    d.If( ~ d.Empty(WeeklyQ1)) # Symptoms are present
    ( WeeklyQ1b ),
    WeeklyQ2,
    d.If(~ d.Empty(WeeklyQ1) # Symptoms are present
         &
         d.Equal(WeeklyQ2, 0)) # Took temp
    ( WeeklyQ2b ),
    d.If(d.Contains(WeeklyQ1, [1])      # Fever among symptoms
         | d.In(WeeklyQ2b, [2,3,4,5]))  # Temp > 37.5
    ( WeeklyQ2c),

    d.If(
#         PREVIOUS_RESPONSE_EXISTS variable goes here
#         &
#         d.Equal(d.Response('WeeklyQ5'), "I am still ill")
#         &
          ~ d.Empty(WeeklyQ1) # Symptoms are present
          )
    ( WeeklyQ3,
      d.If(d.Equal(WeeklyQ3, 0)) ( Message1, WeeklyQ4 ),
      WeeklyQ5,
      WeeklyQ6,
      d.If(d.Equal(WeeklyQ6, 1)) ( WeeklyQ6b ),
      WeeklyQ7,
      d.If(d.Contains(WeeklyQ7, [3])) ( WeeklyQ7b ),
      WeeklyQ8,
      d.If(d.Equal(WeeklyQ8, 2)) ( WeeklyQ8b, WeeklyQ8c,)),
    
    WeeklyQ9a,
    WeeklyQ9b,

#    d.If(~ d.Equal(d.Profile(IntakeQ9), 0)) # reported no seasonal flu jab
#    ( WeeklyQ10 ),
#    # Possibly update IntakeQ9 here?

    WeeklyQ11,
    )

  # TODO tidy up this syntax: see survey.py lines 100-125
  prefill = { WeeklyQ4:  d.Equal(WeeklyQ3, 0),
              WeeklyQ5:  d.Equal(WeeklyQ3, 0),
              WeeklyQ6:  d.Equal(WeeklyQ3, 0),
              WeeklyQ6b: d.Equal(WeeklyQ3, 0),
              WeeklyQ7:  d.Equal(WeeklyQ3, 0),
              WeeklyQ7b: d.Equal(WeeklyQ3, 0),
              WeeklyQ8:  d.Equal(WeeklyQ3, 0),
              WeeklyQ8b: d.Equal(WeeklyQ3, 0),
              WeeklyQ8c: d.Equal(WeeklyQ3, 0),
              WeeklyQ9a: d.Equal(WeeklyQ3, 0),
              WeeklyQ9b: d.Equal(WeeklyQ3, 0),
              }

