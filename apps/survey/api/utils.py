from apps.survey.models import SurveyUser, Survey
from apps.survey.utils import load_specification
from apps.survey.survey import parse_specification
from apps.survey.spec import Question, Branch, Else
from apps.survey.times import epochal_to_timedate
from inspect import isclass
from apps.survey import utils
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
        return reduce(lambda s,o: s+t('option', t('code', o[0]) + t('text', o[1])),
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

class JSONKeyTypeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def check_keys(dir, key_types):
    """key_types is a list of pairs of keys and types. Each key should exist in
    dir and its value shoud be of the corresponding type.
    """
    for key, key_type in key_types:
        if not (key in dir
            and ( key_type == 'any'
                  or isinstance(dir[key], key_type)
                  or ( key_type == str
                       and isinstance(dir[key], unicode)))):
            raise JSONKeyTypeError({'status': 1,
                                    'error': "key '%s' is %s,should be %s" % \
                                    (key, type(dir[key]), repr(key_type))})

def report_data(report):
    """Extract the data corresponding to the fields of report needed to write the
    report to the database.
    """

    # Receive timestamp as in milliseconds since 1970-01-01
    time_stamp = epochal_to_timedate(report['ts'])

    data = report['data']

    try:
        uid = report['uid']
        survey_user = SurveyUser.objects.get(global_id=code_unhash(uid))
    except:
        return {'status': 2, 'error': 'user with activation code not known' % uid}

    try:
        surv_v = report['surv_v']
        survey = Survey.objects.get(survey_id=surv_v)
        spec = load_specification(surv_v)
    except:
        return {'status': 3, 'error': 'survey with id %s not known' % surv_v}
    
    participation = utils.add_survey_participation(survey_user, surv_v)
    utils.add_response_queue(participation, spec, data)
    utils.save_last_response(survey_user, participation, data)
    utils.save_response_locally(survey_user.name, surv_v, data, time_stamp)

    return { 'status': 0, 'prot_v': 0, 'serv' : 0}

def report_survey(jdata):
    """
  {
  "prot_v"      : <<string>>,
  "serv"        : <<int>>,
  "uid"         : <<string>>,
  "reports" [{ "uid"           : <<string>>,
               "surv_v"        : <<string>>,
               "ts"            : <<long>>,
               "data"  [{ "id"        : <<string>>,
                          "value"     : depends on question type
                       }]
            }]
       }
  """

    try:
        # Check presence and types of top-level keys
        check_keys(jdata, [ ('prot_v', str), ('serv', int),
                                                ('uid', str), ('reports', list) ])

        # Check presence and types of reports' keys
        for report in jdata['reports']:
            check_keys(report, [ ('uid', str), ('surv_v', str),
                                 ('ts', int), ('data', list) ])
            for iv_data in report['data']:
                check_keys(iv_data, [ ('id', str), ('value', 'any') ])

        # Check the types of all question replies.
        for id_value in report['data']:
            id = id_value['id']
            value = id_value['value']
            # TODO Check id is a question in survey
            # TODO Check value is a valid reply to question
    except JSONKeyTypeError as e:
        return e.value

    # Check reporting uid exists
    acode = jdata['uid']
    try:
        reporting_user = SurveyUser.objects.get(global_id=code_unhash(acode))
    except DoesNotExist:
        return {'status': 2,
                'error': 'user with activation code %s not known' % acode}

    # Make field entries
    report_items = [ report_data(report) for report in jdata['reports']]
    agg_stat = reduce(lambda agg_stat, report: agg_stat + report['status'],
                                        report_items, 0)

    return {'status': agg_stat,
            'reporting_user': reporting_user.name,
            'report_items': report_items,
           }

def code_hash(gid, code_length=12):
    """Take a global_id (a UUID string containing '-' symbols).
    Hash it to a string of digits of length code_length.
    """
    # modulo 10**code_length and pad left with zeros
    code_format = ('%%0%dd' % code_length)
    gid_int = int(sub('-', '', gid), 16)
    return code_format % (gid_int % 10**code_length)

class GetError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        self.dict = {'status': self.status, 'error_message': self.message}
    def __str__(self):
        return repr(dict)

def code_unhash(activation_code):
    """Takes an activation code.
    Returns the corresponding global user ID.
    Flags nonexistent codes and code collisions.
    """

    # TODO the loop over all SurveyUser objects below likely does not scale to 20.000 users
    # especially since calls to code_unhash are quite common
    matches = [su.global_id for su in SurveyUser.objects.all()
                         if code_hash(su.global_id) == activation_code]
    l = len(matches)
    if l == 0:
        raise GetError(2, 'user with activation code %s not found' % activation_code)
    elif l > 1:
        raise GetError(3, 'multiple users with activation code %s found' %
                             activation_code)
    else:
        return matches[0]

