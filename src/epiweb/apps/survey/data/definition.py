
class Question:
    pass

class Survey:
    pass

class Value:
    pass

class Empty(d.Value):
    pass

### Base classes

class q:
    class Question:
        pass
    class Survey:
        pass


### Definition

# Questions

class Sex(q.Question):
    question = "Are you male or female?"
    options = ("Male", "Female")

class Children(q.Question):
    question = "How many children have you had?"
    options = range(0, 10)

class Age(q.Question):
    question = "What is your age?"
    options = range(0, 120)

class MarStat(q.Question):
    question = "What is your marital status?"
    options = [
        ("NeverMar", "Never been maried"),
        ("Married" , "Married"),
        ("Separate", "Separated"),
        ("Divorced", "Divorced"),
        ("Widowed" , "Widowed")
    ]

class Spouse(q.Question):
    question = "What is your spouse's age?"
    options = range(0, 120)

class Work(q.Question):
    question = "Are you working for pay or profit?"
    options = ("Yes", "No")

class Radio(q.Question):
    question = "Do you regularly listen to the radio?"
    options = ("Yes", "No")

# Survey

class Survey(q.Survey):
    rules = (
        Sex,
        { (Sex, "is", "Female") : ( 
            Children
        ) },
        Age,
        { (Age, ">", 16): (
            MarStat,
            { ((MarStat, "is", "Married"), "or", (MarStat, "is", "Separate")) : ( 
                Spouse
            ) },
            Work
        ) },
        Radio
    )


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

if __name__ == '__main__':
    sp = SurveyPrinter(Survey)
    sp.init()
    
    print "Questions:"
    sp.print_questions()
    
    print
    print "Conditions:"
    sp.print_conditions()

