from epiweb.apps.survey.survey import parse_specification
from epiweb.apps.survey.spec import Question, Branch, Else
from inspect import isclass

def xmlify_spec(spec):
  """Take a survey specificatin and return it as XML."""
  p = parse_specification(spec)
  print p
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

