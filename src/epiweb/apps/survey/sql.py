from inspect import isclass

from epiweb.apps.survey.models import Survey
from epiweb.apps.survey.survey import parse_specification, Specification
from epiweb.apps.survey.spec import Question

#
# Survey/MongoDB to SQL value mapper
#

class Mapper(object):
    '''Survey/MongoDB to SQL value mapper'''
    def serialize(self):
        raise NotImplementedError()

class OptionsSingleMapper(Mapper):
    def __init__(self, options):
        self.options = options
        self.values = [item[0] for item in options]

    def serialize(self):
        return {'type': 'options-single',
                'values': self.values}

class OptionsMultipleMapper(Mapper):
    def __init__(self, options):
        self.options = options
        
        target = range(len(options))
        source = [item[0] for item in options]
        self.mapping = dict(zip(source, target))

    def serialize(self):
        return {'type': 'options-multiple',
                'mapping': self.mapping}

class YesNoMapper(Mapper):
    def serialize(self):
        return {'type': 'yes-no'}

class DateMapper(Mapper):
    def serialize(self):
        return {'type': 'date'}

class DateOrOptionMapper(Mapper):
    def serialize(self):
        return {'type': 'date-or-option'}

class TableOfSelectMapper(Mapper):
    def __init__(self, choices, rows, cols):
        self.choices = choices
        self.rows = rows
        self.cols = cols

        self.values = [item[0] for item in choices]
        self.nrows = len(rows)
        self.ncols = len(cols)

    def serialize(self):
        return {'type': 'date-or-options',
                'values': self.values,
                'rows': self.nrows,
                'cols': self.ncols}

def _get_options_datatype(options):
    values = [value for value, label in options]
    if all([isinstance(value, int) for value in values]):
        return 'INTEGER'

    max_length = 0
    for value in values:
        length = len('%s' % value)
        if length > max_length:
            max_length = length
    return 'VARCHAR(%s)' % max_length

def get_question_field(question):
    qtype = question.type
    
    if qtype == 'yes-no':
        return [(question.id, 'BIT(1)', question.id)], YesNoMapper()

    elif qtype == 'options-multiple':
        res = []
        for index, data in enumerate(question.options):
            value, label = data
            res.append(['%s_%s' % (question.id, index), 'BIT(1)',
                        '%s: %s' % (question.id, label)])
        return res, OptionsMultipleMapper(question.options)

    elif qtype == 'options-single':
        datatype = _get_options_datatype(question.options)
        return [(question.id, datatype, question.id)], OptionsSingleMapper(question.options)

    elif qtype == 'date':
        return [(question.id, 'DATE', question.id)], DateMapper()

    elif qtype == 'date-or-option':
        # Either a date widget or a checkbox (boolean value)
        return [('%s_date' % question.id, 'DATE',
                 '%s: Date' % question.id),
                ('%s_option' % question.id, 'BIT(1)',
                 '%s: Option' % question.id)], DateOrOptionMapper()

    elif qtype == 'table-of-selects':
        datatype = _get_options_datatype(question.choices)

        res = []
        index = 0
        for row in question.rows:
            for col in question.columns:
                res.append(('%s_%s' % (question.id, index), datatype,
                            '%s: %s - %s' % (question.id, row, col)))
                index += 1

        return res, TableOfSelectMapper(question.choices, question.rows,
                                        question.columns)

    elif qtype == 'table-of-options-single':
        datatype = _get_options_datatype(question.options)

        qta = question.type_args
        if qta and isclass(qta[0]) and issubclass(qta[0], Question):
            options = [value for value, label in qta[0].options]
            if len(qta) > 1 and qta[1] is not None:
                options = qta[1]

            available = [option for option in qta[0].options
                                if option[0] in options]
            rows = [(index, option[1])
                    for index, option in enumerate(available)]

        elif qta and isinstance(qta[0], str):
            rows = [(index, label) for index, label in enumerate(qta)]

        res = []
        for row, label in rows:
            res.append(('%s_%s' % (question.id, row), datatype,
                        '%s: %s' % (question.id, label)))
        return res

    return None

def get_fields(questions):
    res = []
    for question in questions:
        fields = get_question_field(question)
        if fields is not None:
            res += fields
    return res

def _create_table_name(name):
    name = name.replace('-', '_')
    name = name.replace('.', '_')
    return name

def _clean_label(label):
    return ' '.join(map(lambda x: x.strip(), label.splitlines()))

def create_ddl(survey):
    data = parse_specification(survey.specification)
    spec = Specification(data)

    sql = []
    sql.append('CREATE TABLE %s' % _create_table_name(data.id))

    fields = [('id', 'INTEGER auto_increment', 'ID'),
              ('uid', 'CHAR(36)', 'User ID'),
              ('date', 'DATETIME', 'Submission date')]

    fields += get_fields(spec.questions)

    # Field and data type
    max_len = max([len(item[0]) for item in fields])
    strformat = '%%-%ds  %%s' % max_len

    sql_fields = [strformat % (name, datatype)
                  for name, datatype, desc in fields]

    # Add comma, except the last line
    for i in range(len(sql_fields)-1):
        sql_fields[i] += ','

    # Add comment (description)
    max_len = max([len(item) for item in sql_fields])
    strformat = '    %%-%ds  -- %%s' % max_len

    sql_fields = [strformat % (sql_fields[i], _clean_label(fields[i][2]))
                  for i in range(len(sql_fields))]

    sql.append('(\n%s\n)' % '\n'.join(sql_fields))

    sql = ' '.join(sql)

    return sql

