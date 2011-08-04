
class Question:
    def __init__(self):
        # Use the class name as an id if it is not defined
        try:
            getattr(self, 'id')
        except AttributeError:
            self.id = self.__class__.__name__

    private = False
    blank = False

class Survey:
    def __init__(self):
        self._index = 0
        self.questions = []
        self.conditions = {}
        self.revindex = {}
        self.affected = {}
        self.map = {}
        self._class_map = {}
        self._iterate(self.rules)
        self._create_affected_list()

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
                self.map[obj.id] = obj
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
        elif ta == 'instance' and isinstance(a, Question):
            res.append(a)

        if type(b).__name__ == 'tuple':
            res += self._get_questions(b)
        elif tb == 'instance' and isinstance(b, Question):
            res.append(b)

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
        self.values = list(values)

class Empty(Value):
    pass

class Profile(Value):
    def __init__(self, name):
        self.name = name

class Previous(Value):
    def __init__(self, name):
        self.name = name

