from tastypie.resources import ModelResource
from apps.survey.models import Profile, SurveyUser, Survey
from apps.survey.survey import parse_specification
from apps.survey.spec import Question, Branch, Else
from pickle import loads
from inspect import isclass

class EpiwebModelResource(ModelResource):
    class Meta:
        default_format = 'application/json'
        include_resource_uri = False
        allowed_methods = ['get']

def xmlify_spec(spec):
    p = parse_specification(spec)

    def a(s):
        return str(s)

    def t(tag, s):
        return a('<%s>\n' % tag) + a(s) + a('</%s>\n' % tag)

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
    xml = t('survey', xs(p.rules))
    return xml

## EIP resources

class GetUserProfile(EpiwebModelResource):
    """Takes global_id
    Returns name, a_uids, code, report_ts
    """
    class Meta:
        resource_name = 'GetUserProfile'
        queryset = Profile.objects.all()
        # queryset = Profile.objects.filter(user__global_id="193807d8-4a30-4601-9bc5-bc59db1696cd")
        filtering = ['user__global_id']
        # fields = ['data']

    def dehydrate(self, bundle):
        id = bundle.data['id']
        return loads(str(bundle.data['data']))
    
class GetReportSurvey(ModelResource):
    """Takes language int
    Returns survey in XML format
    """
    class Meta:
        resource_name = 'GetReportSurvey'
        queryset = Survey.objects.all()
        fields = ['specification']

    def dehydrate(self, bundle):
        spec = bundle.data['specification']
        xml = xmlify_spec(spec)
        return xml
        # return str(parse_specification(bundle.data['specification']))

class Report(ModelResource):
    """Takes uid and reportS
    Returns status
    """
    class Meta:
        queryset = SurveyUser.objects.all()
        allowed_methods = ['put']

