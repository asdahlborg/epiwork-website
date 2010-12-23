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
  id = 'contact-survey-1.0'
  title = 'Contact survey'
  
  rules = ( ContactQ1,
            ContactQ2,
            ContactQ3,
            ContactQ4,
            )
