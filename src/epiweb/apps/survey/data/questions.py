
class Survey:
    def __init__(self):
        self.sections = []

class Section:
    def __init__(self, title=None):
        self.title = title
        self.questions = []

class Question:
    def __init__(self, id, label):
        self.id = id
        self.label = label
        self.type = 'text'
        self.length = '250'
        self.options = []
        self.condition = None

