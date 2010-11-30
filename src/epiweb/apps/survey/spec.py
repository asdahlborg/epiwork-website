import simplejson as json

__all__ = ['Survey', 'Question', 'Profile', 'Response',
           'Advise',
           'If', 'ElseIf', 'Else',
           'Empty', 'Equal', 'EqualIndex', 'In',
           'And', 'Or', 'Not']

class Question(object):
    question = None
    type = None
    private = False
    blank = False

    def __init__(self):
        if not hasattr(self, 'id'):
            self.id = self.__class__.__name__
        if self.question is None:
            raise SpecSyntaxError('Question for Question %s is not specified' % self.id)
        if self.type is None:
            raise SpecSyntaxError('Type for Question %s is not specified' % self.id)

    parent = None

    def visible(self, values):
        parent = self.parent

        while True:
            # top level questions
            if parent is None:
                return True

            # under Else
            elif isinstance(parent, Else):
                # print '>>> Else: prev:', parent.prev
                pass

            # the direct If/ElseIf parent should evaluate to True
            elif not parent.condition.eval(values):
                return False

            # the adjacent If/ElseIf shoudl evaluate to False
            while parent.prev is not None:
                parent = parent.prev
                if parent.condition.eval(values):
                    return False

            # arrives at the first If, then go to its parent
            parent = parent.parent

    def get_condition(self):
        parent = self.parent
        condition = TrueValue()
        while parent is not None:
            if not isinstance(parent, Else):
                condition = condition & parent.condition
            while parent.prev is not None:
                parent = parent.prev
                condition = condition & ~parent.condition
            parent = parent.parent
        return condition

    def get_usage(self, name):
        # print '> get usage:', name
        items = []
        parent = self.parent
        while parent is not None:
            if not isinstance(parent, Else):
                items += parent.get_usage(name)
            while parent.prev is not None:
                parent = parent.prev
                items += parent.get_usage(name)
            parent = parent.parent
        return list(set(items))

    def get_modifier(self):
        return self.get_usage('question')
    def get_profiles(self):
        return self.get_usage('profile')
    def get_responses(self):
        return self.get_usage('response')

    def __str__(self):
        return '<Question [%s]: %s>' % (self.id, self.question)

class Advise(Question):
    type = 'advise'
    message = None

    def __init__(self):
        if not hasattr(self, 'id'):
            self.id = self.__class__.__name__
        if self.message is None:
            raise SpecSyntaxError('Message for Advise %s is not specified' % self.id)
        self.question = self.message
        super(Advise, self).__init__()

class Survey(object):
    id = None
    rules = None
    prefill = {}
    '''
    rules contains Question /class/ or Branch /objects/
    '''

    def __str__(self):
        return '<Survey [%s]>' % self.id

class Profile(object):
    def __init__(self, id):
        """id is question id"""
        self.id = id

    def __str__(self):
        return '<Profile [%s]>' % self.id

class Response(object):
    def __init__(self, id):
        """id is question id"""
        self.id = id

    def __str__(self):
        return '<Response [%s]>' % self.id

##################

class SpecSyntaxError(Exception):
    pass

class Boolean(object):
    '''
    Contains an expression that can be evaluated to a True/False value
    '''
    def eval(self, values):
        raise NotImplementedError()

    def __and__(self, other):
        return And(self, other)
    def __or__(self, other):
        return Or(self, other)
    def __invert__(self):
        return Not(self)

    def get_usage(self, name):
        return []

class Evaluator(Boolean):
    pass

class QuestionClass(object):
    '''
    Holds a class name of a question.

    The id of the class will be resolved when evaluation time.
    '''
    def __init__(self, name):
        '''
        :param: Question name
        '''
        self.name = name

#
# Value evaluator
#

class Value(object):
    def value(self, values):
        raise NotImplementedError()

    def get_usage(self, name):
        return []

class QuestionValue(Value):
    def __init__(self, name):
        self.type = None
        self.name = name
        if type(name) == str:
            self.type = 'id'
        elif type(name) == QuestionClass:
            self.name = name.name
            self.type = 'cls'
        elif issubclass(name, Advise):
            self.name = name.__name__
            self.type = 'advise'
        elif issubclass(name, Question):
            self.name = name.__name__
            self.type = 'cls'
        else:
            raise SpecSyntaxError()
    def value(self, values):
        if self.type == 'id':
            return values[self.name]
        elif self.type == 'advise':
            return True
        elif self.type == 'cls':
            id = values['+id'][self.name]
            return values[id]

    def __str__(self):
        return '<Question [%s]>' % self.name

    @property
    def js(self):
        return 'd.Question(%s)' % json.dumps(self.name)

    def get_usage(self, name):
        if name == 'question':
            return [self.name]
        return []

class ProfileValue(Value):
    def __init__(self, id):
        # print '@@@', id
        self.id = id
    def value(self, values):
        return values['+p'][self.id]

    def __str__(self):
        return '<Profile [%s]>' % self.id

    @property
    def js(self):
        return 'd.Profile(%s)' % json.dumps(self.id)

    def get_usage(self, name):
        # print '@@@ >>>>>>>>', name
        if name == 'profile':
            return [self.id]
        return []

class ResponseValue(Value):
    def __init__(self, id):
        self.id = id
    def value(self, values):
        return values['+r'][self.id]

    def __str__(self):
        return '<Response [%s]>' % self.id

    @property
    def js(self):
        return 'd.Response(%s)' % json.dumps(self.id)

    def get_usage(self, name):
        # print '@@@ >>>>>>>>', name
        if name == 'response':
            return [self.id]
        return []

class Primitive(Value):
    def __init__(self, value):
        self.val = value
    def value(self, values):
        return self.val

    def __str__(self):
        return '<Primitive [%s]>' % json.dumps(self.val)

    @property
    def js(self):
        if type(self.val) in [list, type, set]:
            return json.dumps(list(self.val))
        else:
            return json.dumps(self.val)

class Empty(Evaluator):
    """Check if value is empty"""
    def __init__(self, a):
        """a is Profile object, Response object, Question class or question id"""
        if isinstance(a, Profile):
            self.a = ProfileValue(a.id)
        elif isinstance(a, Response):
            self.a = ResponseValue(a.id)
        else:
            self.a = QuestionValue(a)
    def eval(self, values):
        value = self.a.value(values)
        if type(value) in [list, set, tuple]:
            return len(value) == 0
        else:
            return value is None

    def __str__(self):
        return '<Empty [%s]>' % (self.a,)

    @property
    def js(self):
        return 'd.Empty(%s)' % self.a.js

    def get_usage(self, name):
        return self.a.get_usage(name)

class Equal(Evaluator):
    """Check if the two values are equal"""
    def __init__(self, a, b):
        """a is Profile object, Response object, Question class or question id
           b is Question class or primitives"""
        if isinstance(a, Profile):
            self.a = ProfileValue(a.id)
        elif isinstance(a, Response):
            self.a = ResponseValue(a.id)
        else:
            self.a = QuestionValue(a)

        if type(b) in [str, int, float]:
            self.b = Primitive(b)
        elif isinstance(b, Profile):
            self.b = ProfileValue(b.id)
        elif isinstance(b, Response):
            self.b = ResponseValue(b.id)
        elif issubclass(b, Question):
            self.b = QuestionValue(b)
        else:
            raise SpecSyntaxError()
    def eval(self, values):
        return self.a.value(values) == self.b.value(values) or \
               str(self.a.value(values)) == str(self.b.value(values)) # FIXME XXX

    def __str__(self):
        return '<Equal [%s] [%s]>' % (self.a, self.b)

    @property
    def js(self):
        return 'd.Equal(%s, %s)' % (self.a.js, self.b.js)

    def get_usage(self, name):
        # print 'Equal: get_usage:', name, repr(self.a), repr(self.b)
        return self.a.get_usage(name) + self.b.get_usage(name)
E = Equal

class EqualIndex(Equal):
    def __init__(self, a, index, b):
        super(EqualIndex, self).__init__(a, b)
        self.index = index

    def eval(self, values):
        a = int(self.a.value(values)[self.index])
        b = self.b.value(values)
        return a == b

    @property
    def js(self):
        return 'd.EqualIndex(%s, %s, %s)' % (self.a.js, self.index, self.b.js)


class In(Evaluator):
    """Check if the first value is one of the second values"""
    def __init__(self, a, b):
        """a is Profile object, Response object, Question class or question id
           b is list/set/tuple of primitives"""
        if isinstance(a, Profile):
            self.a = ProfileValue(a.id)
        elif isinstance(a, Response):
            self.a = ResponseValue(a.id)
        else:
            self.a = QuestionValue(a)

        if not type(b) in [tuple, list, set]:
            raise SpecSyntaxError()
        if not all([type(val) in [str, int, float] for val in b]):
            raise SpecSyntaxError()
        self.b = Primitive(list(b))
    def eval(self, values):
        # Force the value of the first argument into a list
        a = self.a.value(values)
        if not type(a) in [list, set, tuple]:
            a = [a]
        res = any([val in a for val in self.b.value(values)])

        # FIXME XXX the value of might be a string instead of integer
        try:
            b = self.b.value(values)
            a = map(int, a)
            res = any([val in a for val in b])
        except ValueError:
            pass
        return res

    def __str__(self):
        return '<In [%s] [%s]>' % (self.a, self.b)

    @property
    def js(self):
        return 'd.In(%s, %s)' % (self.a.js, self.b.js)

    def get_usage(self, name):
        return self.a.get_usage(name) + self.b.get_usage(name)

class Compare(Evaluator):
    def __init__(self, **comparisons):
        """key is Question class name
           value is Question class or primitives"""
        self.comparisons = []
        for key, val in comparisons.items():
            key = QuestionValue(QuestionClass(key))
            if type(val) in [str, int, float]:
                val = Primitive(val)
            elif issubclass(val, Question):
                val = QuestionValue(val)
            else:
                raise SpecSyntaxError()
            self.comparisons.append(Equal(key, val))
    def eval(self, values):
        return all([comparison.eval(value) for comparison in self.comparisons])

    def __str__(self):
        return '<Compare [%s]>' % ' '.join([str(comparison) for comparison in self.comparisons])

    @property
    def js(self):
        if len(self.comparisons) == 1:
            return self.comparisons[0].js
        return '(%s)' % (') && ('.join([comparison.js for comparison in self.comparisons]))

    def get_usage(self, name):
        return reduce(lambda a, b: (a + b),
                      [comparison.get_usage(name) for comparison in self.comparisons])

#
# Consts
#

class TrueValue(Boolean):
    def eval(self, values):
        return True

    def __str__(self):
        return '<TrueValue>'

    @property
    def js(self):
        return 'd.BooleanTrue()';

#
# Operators
#

class And(Boolean):
    '''
    AND operator
    '''
    def __init__(self, a, *conditions):
        conditions = [a] + list(conditions)
        if not all([isinstance(condition, Boolean) for condition in conditions]):
            raise SpecSyntaxError()
        self.conditions = conditions
    def eval(self, values):
        return all([condition.eval(values) for condition in self.conditions])

    def __str__(self):
        return '<And [%s]>' % ('] ['.join([str(condition) for condition in self.conditions]))

    @property
    def js(self):
        if len(self.conditions) == 1:
            return self.conditions[0].js
        return 'd.And(%s)' % (', '.join([condition.js for condition in self.conditions]))

    def get_usage(self, name):
        return reduce(lambda a, b: (a + b),
                      [condition.get_usage(name) for condition in self.conditions])

class Or(Boolean):
    '''
    OR operator
    '''
    def __init__(self, a, *conditions):
        conditions = [a] + list(conditions)
        if not all([isinstance(condition, Boolean) for condition in conditions]):
            raise SpecSyntaxError()
        self.conditions = conditions
    def eval(self, values):
        return any([condition.eval(values) for condition in self.conditions])

    def __str__(self):
        return '<Or [%s]>' % ('] ['.join([str(condition) for condition in self.conditions]))

    @property
    def js(self):
        if len(self.conditions) == 1:
            return self.conditions[0].js
        return 'd.Or(%s)' % (', '.join([condition.js for condition in self.conditions]))

    def get_usage(self, name):
        return reduce(lambda a, b: (a + b),
                      [condition.get_usage(name) for condition in self.conditions])

class Not(Boolean):
    '''
    NOT operator
    '''
    def __init__(self, condition):
        if not isinstance(condition, Boolean):
            raise SpecSyntaxError()
        self.condition = condition
    def eval(self, values):
        return not self.condition.eval(values)

    def __str__(self):
        return '<Not [%s]>' % self.condition

    @property
    def js(self):
        return 'd.Not(%s)' % self.condition.js

    def get_usage(self, name):
        # print 'not get usage:', name
        return self.condition.get_usage(name)

#
# Branching
#

class Branch(object):
    '''
    Conditional branching
    '''
    prev = None
    parent = None

    def get_usage(self, name):
        return []

class BranchIf(Branch):
    def __init__(self, condition, rules):
        self.condition = condition
        self.rules = validate_rules(rules, self)
    def get_usage(self, name):
        return self.condition.get_usage(name)

class BranchElseIf(Branch):
    def __init__(self, condition, rules):
        self.condition = condition
        self.rules = validate_rules(rules, self)
    def get_usage(self, name):
        return self.condition.get_usage(name)

class Conditional(object):
    '''
    Conditional branching generator
    '''
    pass

class If(Conditional):
    def __init__(self, condition, *conditions):
        conds = [condition] + list(conditions)
        if not all([isinstance(cond, Boolean) for cond in conds]):
            raise SpecSyntaxError()
        self.conditions = And(*conds)

    def __call__(self, *rules):
        if len(rules) == 0:
            raise SpecSyntaxError()
        return BranchIf(self.conditions, rules)

class ElseIf(Conditional):
    def __init__(self, condition, *conditions):
        conds = [condition] + list(conditions)
        if not all([isinstance(cond, Boolean) for cond in conds]):
            raise SpecSyntaxError()
        self.conditions = And(*conds)

    def __call__(self, *rules):
        if len(rules) == 0:
            raise SpecSyntaxError()
        return BranchElseIf(self.conditions, rules)

class Else(Conditional, Branch):
    def __init__(self, *rules):
        if len(rules) == 0:
            raise SpecSyntaxError()
        self.rules = validate_rules(rules, self)


#
# Rule validator
#

def validate_rules(rules, parent=None):
    res = []
    prev = None
    for rule in rules:
        # print '>', rule
        if issubclass(rule.__class__, Branch):
            # branch object
            klass = rule.__class__
            if klass == BranchIf:
                rule.prev = None
                prev = rule
            elif klass == BranchElseIf:
                if prev is None:
                    raise SpecSyntaxError()
                rule.prev = prev
                prev = rule
            elif klass == Else:
                if prev is None:
                    raise SpecSyntaxError()
                rule.prev = prev
                prev = None
            res.append(rule)

        elif issubclass(rule, Question):
            # question class
            res.append(rule)
            last = None
        else:
            raise SpecSyntaxError()

        rule.parent = parent

    return res

