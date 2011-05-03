from datetime import datetime, date
from inspect import isclass

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
        self.values = [item[0] for item in options]

    def serialize(self):
        return {'type': 'options-multiple',
                'values': self.values}

class TypeMapper(Mapper):
    type = None
    def __init__(self, type=None):
        if type is not None:
            self.type = type

    def serialize(self):
        if self.type is None:
            raise ValueError('Invalid mapper type')
        return {'type': self.type}

class YesNoMapper(TypeMapper):
    type = 'yes-no'

class DateMapper(TypeMapper):
    type = 'date'

class DateOrOptionMapper(TypeMapper):
    type = 'date-or-option'

class MonthYearMapper(TypeMapper):
    type = 'month-year'

class PostCodeMapper(TypeMapper):
    type = 'postcode'

class TableOfSelectsMapper(Mapper):
    def __init__(self, choices, rows, cols):
        self.choices = choices
        self.rows = rows
        self.cols = cols

        self.values = [item[0] for item in choices]
        self.nrows = len(rows)
        self.ncols = len(cols)

    def serialize(self):
        return {'type': 'table-of-selects',
                'values': self.values,
                'rows': self.nrows,
                'cols': self.ncols}

class TableOfOptionsSingleMapper(Mapper):
    def __init__(self, options, rows):
        self.options = options
        self.rows = rows

        self.values = [item[0] for item in options]
        self.nrows = len(rows)

    def serialize(self):
        return {'type': 'table-of-options-single',
                'values': self.values,
                'rows': self.nrows}

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

        return res, TableOfSelectsMapper(question.choices, question.rows,
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

        else:
            raise ValueError('Invalid question: %s' % question.id)

        res = []
        for row, label in rows:
            res.append(('%s_%s' % (question.id, row), datatype,
                        '%s: %s' % (question.id, label)))
        return res, TableOfOptionsSingleMapper(question.options, rows)

    elif qtype == 'month-year':
        return [(question.id, 'DATE', question.id)], MonthYearMapper()

    elif qtype == 'postcode':
        return [(question.id, 'VARCHAR(25)', question.id)], PostCodeMapper()

    return None, None

def get_fields(questions):
    res = []
    mappers = {}
    for question in questions:
        fields, mapper = get_question_field(question)
        if fields is not None:
            res += fields
            mappers[question.id] = mapper
    return res, mappers

def create_table_name(name):
    name = name.replace('-', '_')
    name = name.replace('.', '_')
    return name

def _clean_label(label):
    return ' '.join(map(lambda x: x.strip(), label.splitlines()))

def create_sql_create(spec):
    sql = []
    sql.append('CREATE TABLE %s' % create_table_name(spec.survey.id))

    fields, mappers = get_fields(spec.questions)

    fields[0:0] = [('id', 'INTEGER auto_increment PRIMARY KEY', 'ID'),
                   ('_id', 'CHAR(36)', 'User ID'),
                   ('uid', 'CHAR(36)', 'User ID'),
                   ('date', 'DATETIME', 'Submission date')]
    mappers['_id'] = TypeMapper('id')
    mappers['#uid'] = TypeMapper('uid')
    mappers['#date'] = TypeMapper('submission-date')

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

    # Mapper
    mapper_data = dict([(key, mapper.serialize())
                        for key, mapper in mappers.items()])
    mapper_info = {'survey_id': spec.survey.id,
                   'mapping': mapper_data}

    return sql, mapper_info

def create_insert_sql_fields(mappers, data):
    fields = {}

    for key, value in data.items():
        if key in mappers:
            fields.update(mappers[key](value))

    return fields

def create_insert_sql(table, mappers, data):
    pairs = create_insert_sql_fields(mappers, data)
    if len(pairs) == 0:
        return '', ()

    fields, values = zip(*pairs.items())

    sql = 'INSERT INTO %s (%s) VALUES (%s)' % \
          (table, ', '.join(fields), ', '.join(['%s'] * len(fields)))

    return sql, values

def get_mapper(field, data):
    mtype = data['type']

    if mtype == 'options-single':
        values = set(data['values'])
        def func(value):
            if value not in values:
                raise ValueError
            return {field: value}
        return func

    elif mtype == 'options-multiple':
        def func(values):
            if not type(values) in [list, tuple, set]:
                values = [values]

            mapping = dict(zip(data['values'], range(len(data['values']))))

            res = {}
            for value in values:
                if not value in mapping:
                    raise ValueError

                column = '%s_%s' % (field, mapping[value])
                res[column] = 1

            return res
        return func

    elif mtype == 'yes-no':
        def func(value):
            '''Convert True/1/yes to 1 and the rest to 0'''
            res = 0
            if value is True or str(value).lower() in ['yes', '1']:
                res = 1
            return {field: res}
        return func

    elif mtype == 'date':
        def func(value):
            return {field: value}
        return func

    elif mtype == 'date-or-option':
        def func(value):
            if isinstance(value, datetime) or isinstance(value, date):
                return {'%s_date' % field: value}
            return {'%s_option' % field: 1}
        return func

    elif mtype == 'table-of-selects':
        def func(values):
            if not type(values) in [list, set, tuple]:
                raise ValueError, 'Invalid data'
            if len(values) != data['rows'] * data['cols']:
                raise ValueError, 'Invalid number of data'

            res = {}
            for index, value in enumerate(values):
                if not value in data['values']:
                    raise ValueError, 'Invalid value'
                res['%s_%s' % (field, index)] = value
            return res
        return func

    elif mtype == 'table-of-options-single':
        def func(values):
            if not type(values) in [list, set, tuple]:
                raise ValueError, 'Invalid data'
            if len(values) != data['rows']:
                raise ValueError, 'Invalid number of data'

            res = {}
            for index, value in enumerate(values):
                if not value in data['values']:
                    raise ValueError, 'Invalid value'
                res['%s_%s' % (field, index)] = value

            return res

        return func

    elif mtype == 'month-year':
        def func(values):
            return {field: values}
        return func

    elif mtype == 'postcode':
        def func(values):
            return {field: values}
        return func

    elif mtype == 'id':
        def func(values):
            return {field: values}
        return func

    elif mtype == 'uid':
        def func(values):
            return {'uid': values}
        return func

    elif mtype == 'submission-date':
        def func(values):
            return {'date': values}
        return func

def create_mappers(mapper_data):
    mappers = {}

    for field, data in mapper_data.items():
        mappers[field] = get_mapper(field, data)

    return mappers

def test():
    mapper_data = {
        'Q01': { 'type': 'yes-no'},
        'Q02': { 'type': 'options-multiple', 'values': [0,3,4,5,2,1]},
        'Q03': { 'type': 'options-single', 'values': [0,1,2,3]},
        'Q04': { 'type': 'date'},
        'Q05': { 'type': 'date-or-option'},
        'Q06': { 'type': 'month-year'},
        'Q07': { 'type': 'postcode'},
        'Q08': { 'type': 'table-of-selects', 'rows': 2, 'cols': 4, 'values': [0,1,2]},
        'Q09': { 'type': 'table-of-options-single', 'rows': 3, 'values': [0,1,2,3,4,5]},
    }
    mappers = create_mappers(mapper_data)

    data = {
        'Q01': 'Yes',
        'Q02': [2,1,3],
        'Q03': 3,
        'Q04': date(2011, 10, 2),
        'Q05': 0,
        'Q06': date(2000, 10, 2),
        'Q07': '1234AB',
        'Q08': [0,1, 2,0, 1,2, 0,1],
        'Q09': [0,1,2],
    }
    sql, values = create_insert_sql('TargetTable', mappers, data)
    return sql, values

