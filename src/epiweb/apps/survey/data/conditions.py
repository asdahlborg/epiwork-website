
__all__ = ['Q', 'Intake', 'OneOf', 'NotEmpty']

class Statement:
    def evaluate(self):
        raise NotImplementedError()

class Atom:
    def value(self):
        raise NotImplementedError()
    def __eq__(self, other):
        return Compare(self, other, 'eq')
    def __ne__(self, other):
        return Compare(self, other, 'ne')
    def __lt__(self, other):
        return Compare(self, other, 'lt')
    def __le__(self, other):
        return Compare(self, other, 'le')
    def __gt__(self, other):
        return Compare(self, other, 'gt')
    def __ge__(self, other):
        return Compare(self, other, 'lt')

class Compare(Statement):
    def __init__(self, a, b, op):
        self.a = a
        self.b = b
        self.op = op
    def __and__(self, other):
        return Compare(self, other, 'and')
    def __or__(self, other):
        return Compare(self, other, 'or')

class NotEmpty(Compare):
    def __init__(self, a):
        self.a = a

class OneOf(Compare):
    def __init__(self, a, options):
        self.a = a
        self.options = options

class Q(Atom):
    def __init__(self, id):
        self.id = id

class Intake(Atom):
    def __init__(self, id):
        self.id = id

