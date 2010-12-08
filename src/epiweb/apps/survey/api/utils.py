from epiweb.apps.survey.models import SurveyUser, Survey
from epiweb.apps.survey.utils import load_specification
from epiweb.apps.survey.survey import parse_specification
from epiweb.apps.survey.spec import Question, Branch, Else
from epiweb.apps.survey.times import epochal_to_timedate
from inspect import isclass
from re import sub

def xmlify_spec(spec):
  """Take a survey specificatin and return it as XML."""
  p = parse_specification(spec)
  def a(s):
    return str(s)

  def t(tag, s, attrs=[]):
    attrstr = ''
    for (n,v) in attrs:
      attrstr += ' %s="%s"' % (n, v)
    return a('<%s%s>\n' % (tag, attrstr)) + a(s) + a('\n</%s>' % tag)

  def xo(options):
    return reduce(lambda s,o: s+t('option', t('code', o[0]) + t('text', o[1])) ,
                  options, '')

  def xs(f):
    if not f:
      return ''
    if isinstance(f, str):
      return f + '\n'
    if isinstance(f, list) or isinstance(f, tuple):
      return xs(f[0]) + xs(f[1:])
    elif isinstance(f, Else):
      return t('else', f.rules)
    elif isinstance(f, Branch):
      # Process condition here!!!
      return t('branch', t('condition', f.condition) + t('rules', f.rules))
    elif isclass(f) and issubclass(f, Question):
      x = t('type', f.type)
      x += t('question', f.question)
      if 'options' in dir(f):
        x += xo(f.options)
      return t('item', x)
    else:
      t('unknown', type(f))

  xml = '<?xml version="1.0"?>\n' + t('survey', xs(p.rules))
  return xml

def check_keys(dir, key_types):
  """key_types is a list of pairs of keys and types. Each key should exist in
  dir and its value shoud be of the corresponding type.
  """
  for key, key_type in key_types:
    if not (key in dir and isinstance(dir[key], key_type)):
      return {'status': 1,
              'error': 'key %s should be of type %s' % (key, key_type)}

def report_data(report):
  """Extract the data corresponding to the fields of report needed to write the
  report to the database.
  """
  # Receive timestamp as in milliseconds since 1970-01-01
  time_stamp = epochal_to_timedate(report['ts'])

  uid = report['uid']
  survey_user = SurveyUser.objects.get(global_id=uid)
  if not survey_user:
    return  {'status': 2, 'error': 'user with global_id %s not known' % uid}

  surv_v = report['surv_v']
  survey_id = Survey.objects.get(survey_id=surv_v)
  if not survey_id:
    return  {'status': 3, 'error': 'survey with id %s not known' % surv_v}
  spec = load_specification(surv_v)
  
  # Build form.cleaned_data
  
  # survey_id.specification now contains the source text of the survey file.

  return { 'survey_user': survey_user.name,
           'time_stamp': time_stamp,
           'survey_id': survey_id.survey_id,
           'spec': spec.questions, }

def report_survey(jdata):
  """
  {
  "prot_v"      : <<string>>,
  "serv"        : <<int>>,
  "uid"         : <<string>>,
  "reports" [{ "uid"           : <<string>>,
               "surv_v"        : <<string>>,
               "ts"            : <<long>>,
               "data"  [{ "id"        : <<int>>,
                          "value"     : [<<<string>>]
                       }]
            }]
       }
  """
  
  # Check presence and types of top-level keys
  check_keys(jdata, [ ('prot_v', str), ('serv', int),
                      ('uid', str), ('reports', list) ])

  # Check presence and types of reports' keys
  for report in jdata['reports']:
    check_keys(report, [ ('uid', str), ('surv_v', str),
                         ('ts', long), ('data', list) ])

    for iv_data in report['data']:
      check_keys(iv_data, [ ('id', int), ('value', list) ])

  # Check the types of all question replies.
  for id_value in report['data']:
    id = id_value['id']
    value = id_value['value']
    # TODO Check id is a question in survey
    # TODO Check value is a valid reply to question

  # Check reporting uid exists
  uid = jdata['uid']
  reporting_user = SurveyUser.objects.get(global_id=uid)
  if not reporting_user:
    return  {'status': 2, 'error': 'user with global_id %s not known' % uid}


  # Make field entries
  report_items = [ report_data(report) for report in jdata['reports']]

#  participation = utils.add_survey_participation(survey_user, spec.survey.id)
#
#  utils.add_response_queue(participation, spec, form.cleaned_data)
#  data = utils.format_response_data(spec, form.cleaned_data)
#  utils.save_last_response(survey_user, participation, data)

  return {'status': 'completed',
          'reporting_user': reporting_user.name,
          'report_items': report_items,
          }

def code_hash(gid, code_length=12):
  """Take a global_id (a UUID string containing '-' symbols).
  Hash it to a string of digits of length code_length.
  """
  # divide by 10**code_length and pad left with zeros
  code_format = ('%%0%dd' % code_length)
  gid_int = int(sub('-', '', gid), 16)
  return code_format % (gid_int % 10**code_length)
