
def _load_spec(spec):
    from epiweb.apps.survey import definitions
    vars = {'d': definitions}
    exec(spec, vars)
    return vars
    
def parse(spec, survey_class='Survey'):
    vars = _load_spec(spec)
    klass = vars[survey_class]
    return klass()

