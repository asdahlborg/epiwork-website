
class Question:
    def __init__(self):
        # Use the class name as an id if it is not defined
        try:
            getattr(self, 'id')
        except AttributeError:
            self.id = self.__class__.__name__

class Survey:
    def __init__(self):
        self._index = 0
        self.questions = []
        self.conditions = {}
        self.revindex = {}
        self._class_map = {}
        self._iterate(self.rules)
        self._create_affected_list()

        print self.conditions

    def _iterate(self, root, conditions=[]):
        for rule in root:
            t = type(rule).__name__
            if t == 'classobj' and issubclass(rule, Question):
                self._index += 1
                obj = rule()
                self._class_map[rule] = obj
                self.questions.append(obj)
                self.revindex[obj] = self._index
                self.conditions[obj] = self._instantiate(conditions)
            elif t == 'dict':
                cond = rule.keys()[0]
                sub = rule.values()[0]
                if type(sub).__name__ != 'tuple':
                    sub = rule.values()
                self._iterate(sub, conditions + [cond])

    def _instantiate(self, conds):
        res = []
        for cond in conds:
            a = cond[0]
            b = cond[2]
            ta = type(a).__name__
            tb = type(b).__name__

            if ta == 'tuple':
                a = self._instantiate(a)
            elif ta == 'classobj' and issubclass(a, Question):
                a = self._class_map[a]

            if type(b).__name__ == 'tuple':
                b = self._instantiate(b)
            elif tb == 'classobj' and issubclass(b, Question):
                b = self._class_map[b]

            res.append((a, cond[1], b))

        return res

    def _get_questions(self, cond):
        res = []
        a = cond[0]
        b = cond[2]
        ta = type(a).__name__
        tb = type(b).__name__

        if ta == 'tuple':
            res += self._get_questions(a)
        elif ta == 'classobj' and issubclass(a, Question):
            res.append(self._class_map[a])

        if type(b).__name__ == 'tuple':
            res += self._get_questions(b)
        elif tb == 'classobj' and issubclass(b, Question):
            res.append(self._class_map[b])

        return res
    
    def _create_affected_list(self):
        rev = {}
        self.affected = {}
        for question in self.questions:
            conds = self.conditions[question]
            self.affected[question] = []
            rev[question] = []

            for cond in conds:
                rev[question] += self._get_questions(cond)

        for item in rev:
            for q in rev[item]:
                self.affected[q].append(item)

class Value:
    def get_value(self):
        raise NotImplementedError()

class Items(Value):
    def __init__(self, *values):
        self.values = values

class Empty(Value):
    pass

class Profile(Value):
    def __init__(self, name):
        self.name = name



### Printer

class SurveyPrinter:
    def __init__(self, survey):
        self.survey = survey

    def _serialize(self):
        self.index = 0
        self.questions = []
        self.conditions = {}
        self.revindex = {}
        self._iterate(self.survey.rules)

    def _iterate(self, root, conditions=[]):
        for rule in root:
            t = type(rule).__name__
            if t == 'classobj' and issubclass(rule, q.Question):
                self.index += 1
                self.questions.append(rule)
                self.revindex[rule] = self.index
                self.conditions[rule] = conditions
            elif t == 'dict':
                cond = rule.keys()[0]
                sub = rule.values()[0]
                if type(sub).__name__ != 'tuple':
                    sub = rule.values()
                self._iterate(sub, conditions + [cond])

    def init(self):
        self._serialize()

    def print_questions(self):
        for q in self.questions:
            to = type(q.options).__name__
            if to == 'tuple':
                options = ", ".join(q.options)
            elif to == 'list':
                if type(q.options[0]).__name__ == 'tuple':
                    options = "\n       ".join(map(lambda x: "%s [%s]" % (x[1], x[0]), q.options))
                else:
                    options = "%d..%d" % (q.options[0], q.options[len(q.options)-1]+1)

            print "%2d. %s [%s]\n    => %s" % (self.revindex[q], q.question, q.__name__, options)


    def _repr_condition(self, con):
        a = con[0]
        op = con[1]
        b = con[2]

        ta = type(a).__name__
        tb = type(b).__name__

        if ta == 'tuple':
            a = "(%s)" % self._repr_condition(a)
        elif ta == 'classobj':
            a = a.__name__

        if tb == 'tuple':
            b = "(%s)" % self._repr_condition(b)
        elif tb == 'classobj':
            b = b.__name__

        return "%s %s %s" % (a, op, b)

    def print_conditions(self):
        for q in self.questions:
            cons = self.conditions[q]
            if len(cons) == 0:
                print "%2d. %s => None" % (self.revindex[q], q.__name__)
            else:
                print "%2d. %s =>" % (self.revindex[q], q.__name__)
                for con in cons:
                    print "    - %s" % self._repr_condition(con)

