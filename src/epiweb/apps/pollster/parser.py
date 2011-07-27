from django.db import models
from xml.etree import ElementTree
import re, warnings
import models

def survey_update_from_xml(survey, xmlstring):
    # ElementTree does not like being passed unicode objects
    xmlstring = '<?xml version="1.0" encoding="UTF-8"?>'+xmlstring.encode('utf-8')
    root = ElementTree.XML(xmlstring)

    survey.title = root.find('h1').text or ''
    survey.shortname = root.find('h1').get('data-shortname') or ''
    survey.version = root.find('h1').get('data-version') or ''
    survey.save()

    idmap = {}
    question_ordinal = 1
    question_xrules = []
    for wrapper in root.findall('div'):
        if 'question-wrapper' not in wrapper.get('class'):
            continue
        xquestion = [i for i in wrapper if 'question' in i.get('class')][0]
        question = _update_question_from_xml(survey, idmap, xquestion, question_ordinal)
        question_ordinal += 1

        column_ordinal = 1
        xcolumns = [ul for ul in xquestion.findall('ul') if 'columns' in ul.get('class')] or [[]]
        for xcolumn in xcolumns[0]:
            _update_column_from_xml(survey, idmap, question, xcolumn, column_ordinal)
            column_ordinal += 1

        row_ordinal = 1
        xrows = [ul for ul in xquestion.findall('ul') if 'rows' in ul.get('class')] or [[]]
        for xrow in xrows[0]:
            _update_row_from_xml(survey, idmap, question, xrow, row_ordinal)
            row_ordinal += 1

        option_ordinal = 1
        xoptions = [ul for ul in xquestion.findall('ul') if 'choices' in ul.get('class')] or [[]]
        for xoption in xoptions[0]:
            _update_option_from_xml(survey, idmap, question, xoption, option_ordinal)
            option_ordinal += 1

        xrules = [i for i in wrapper if 'rules' in i.get('class')][0]
        question_xrules.append((question, xrules))

    # After generating correct IDs for all questions and options we process
    # the rules by iterating again the XML tree.

    for question, xrules in question_xrules:
        for xrule in xrules:
            _update_rule_from_xml(survey, idmap, question, xrule)

    survey.save()

def _get_question_id(idmap, idstr):
    return idmap[idstr]

def _get_option_id(idmap, idstr):
    return idmap[idstr]

def _update_question_from_xml(survey, idmap, root, ordinal):
    # Extract question ID and load corresponding question; if it does not exists
    # insert and empty question to generate it. In both cases we have a question
    # to fill with options and rules.
    data_type = root.get('data-data-type')
    open_option_data_type = root.get('data-open-option-data-type')
    tags = root.get('data-tags')
    regex = None
    if root.find('input') is not None:
        regex = root.find('input').get('pattern')
    error_message = ([e.text for e in root.findall('p') if 'error-message' in e.get('class', '')] + [None]) [0]
    data_name = [e.text for e in root.findall('div') if 'info' in e.get('class', '')][0]
    title = [e.text for e in root.findall('p/span') if 'title' in e.get('class', '')][0]
    hidden = 'starts-hidden' in (root.get('class') or '')
    mandatory = 'mandatory' in (root.get('class') or '')
    deleted = 'deleted' in (root.get('class') or '')
    description = ''
    xdescription = root.find('p')
    if xdescription is not None:
        description = (xdescription[-1].tail or '').strip()

    temp_id = root.get('id') or ''
    match = re.match('^question-(\d+)$', temp_id)

    if deleted:
        models.Question.objects.filter(id = int(match.group(1))).delete()
        question = None
    elif match:
        question = models.Question.objects.get(id = int(match.group(1)))
        question.data_name = data_name or ''
        question.title = title or ''
        question.description = description or ''
        question.tags = tags or ''
        question.regex = regex or ''
        question.error_message = error_message or ''
        question.starts_hidden = hidden
        question.is_mandatory = mandatory
        question.ordinal = ordinal
        if data_type:
            question.data_type = models.QuestionDataType.objects.get(id = data_type)
        if open_option_data_type:
            question.open_option_data_type = models.QuestionDataType.objects.get(id = open_option_data_type)
        question.save()
    else:
        question_type = root.get('data-question-type')
        question = models.Question()
        question.survey = survey
        question.type = question_type
        question.data_name = data_name or ''
        question.title = title or ''
        question.description = description or ''
        question.tags = tags or ''
        question.regex = regex or ''
        question.error_message = error_message or ''
        question.starts_hidden = hidden
        question.is_mandatory = mandatory
        question.ordinal = ordinal
        if data_type:
            question.data_type = models.QuestionDataType.objects.get(id = data_type)
        else:
            question.data_type = models.QuestionDataType.objects.get(id = 1)
        if open_option_data_type:
            question.open_option_data_type = models.QuestionDataType.objects.get(id = open_option_data_type)
        question.save()
    idmap[temp_id] = question and question.id
    return question

def _update_column_from_xml(survey, idmap, question, root, ordinal):
    temp_id = root.get('id') or ''
    match = re.match('^column-(\d+)$', temp_id)
    deleted = 'deleted' in (root.get('class') or '')
    if deleted or question is None:
        models.QuestionColumn.objects.filter(id = int(match.group(1))).delete()
        column = None
    else:
        title = [e.text for e in root.findall('span') if 'title' in e.get('class', '')][0]
        if match:
            column = models.QuestionColumn.objects.get(id = int(match.group(1)))
            column.title = title or ''
            column.ordinal = ordinal
            column.save()
        else:
            column = models.QuestionColumn()
            column.question = question
            column.title = title or ''
            column.ordinal = ordinal
            column.save()
    idmap[temp_id] = column and column.id
    return column

def _update_row_from_xml(survey, idmap, question, root, ordinal):
    temp_id = root.get('id') or ''
    match = re.match('^row-(\d+)$', temp_id)
    deleted = 'deleted' in (root.get('class') or '')
    if deleted or question is None:
        models.QuestionRow.objects.filter(id = int(match.group(1))).delete()
        row = None
    else:
        title = [e.text for e in root.findall('span') if 'title' in e.get('class', '')][0]
        if match:
            row = models.QuestionRow.objects.get(id = int(match.group(1)))
            row.title = title or ''
            row.ordinal = ordinal
            row.save()
        else:
            row = models.QuestionRow()
            row.question = question
            row.title = title or ''
            row.ordinal = ordinal
            row.save()
    idmap[temp_id] = row and row.id
    return row

def _update_option_from_xml(survey, idmap, question, root, ordinal):
    # If we have an <input> tag, then this is a real option, else it is
    # a virtual option and we read the range/regexp data directly from
    # the <li> element. We also look for the option id, to decide if this
    # is an old option to update or a new one to create.
    temp_id = root.get('id') or ''
    match = re.match('^option-(\d+)$', temp_id)
    xinput = root.find('input')
    hidden = 'starts-hidden' in (root.get('class') or '')
    is_open = 'open' in (root.get('class') or '')
    deleted = 'deleted' in (root.get('class') or '')
    if deleted or question is None:
        models.Option.objects.filter(id = int(match.group(1))).delete()
        option = None
    elif xinput is not None:
        text = root.find('label').text
        value = xinput.get('value')
        if match:
            option = models.Option.objects.get(id = int(match.group(1)))
            option.starts_hidden = hidden
            option.is_open = is_open
            option.text = text or ''
            option.value = value or ''
            option.ordinal = ordinal
            option.name = "%s_%s" % (question.data_name, option.id)
            option.save()
        else:
            option = models.Option()
            option.question = question
            option.is_virtual = False
            option.starts_hidden = hidden
            option.is_open = is_open
            option.text = text or ''
            option.value = value or ''
            option.ordinal = ordinal
            option.save()
            # to update the name we need the generated option id.
            option.name = "%s_%s" % (question.data_name, option.id)
            option.save()
    else:
        type_id = root.get('data-type')
        value = root.get('data-value')
        inf = root.get('data-inf')
        sup = root.get('data-sup')
        regex = root.get('data-regex')
        if match:
            option = models.Option.objects.get(id = int(match.group(1)))
            option.virtual_type = models.VirtualOptionType.objects.get(id=int(type_id))
            option.virtual_inf = inf or ''
            option.virtual_sup = sup or ''
            option.virtual_regex = regex or ''
            option.value = value or ''
            option.starts_hidden = hidden
            option.ordinal = ordinal
            option.name = "%s_%s" % (question.data_name, option.id)
            option.save()
        else:
            option = models.Option()
            option.question = question
            option.is_virtual = True
            option.virtual_inf = inf or ''
            option.virtual_sup = sup or ''
            option.virtual_regex = regex or ''
            option.value = value or ''
            option.starts_hidden = hidden
            option.ordinal = ordinal
            option.save()
            # to update the name we need the generated option id.
            option.name = "%s_%s" % (question.data_name, option.id)
            option.save()
    idmap[temp_id] = option and option.id
    return option

def _update_rule_from_xml(survey, idmap, question, root):
    temp_id = root.get('id') or ''
    match = re.match('^rule-(\d+)$', temp_id)
    type_id = root.get('data-type')
    deleted = 'deleted' in (root.get('class') or '')

    subject_option_ids = [_get_option_id(idmap, id) for id in root.get('data-subject-options', '').split()]
    subject_option_ids = [id for id in subject_option_ids if id is not None]
    object_question_id = _get_question_id(idmap, root.get('data-object-question'))
    object_option_ids = [_get_option_id(idmap, id) for id in root.get('data-object-options', '').split()]
    object_option_ids = [id for id in object_option_ids if id is not None]

    if not deleted and not type_id and not object_question_id:
        warnings.warn('unable to create rule in question %s (triggers %s, question %s)' % (question.id, subject_option_ids, object_question_id))
        return None

    if deleted or question is None or object_question_id is None:
        models.Rule.objects.filter(id = int(match.group(1))).delete()
        rule = None
    elif match:
        rule = models.Rule.objects.get(id = int(match.group(1)))
        rule.rule_type = models.RuleType.objects.get(id = int(type_id))
        rule.subject_question = question
        rule.object_question = models.Question.objects.get(id = object_question_id)
        rule.save()
        rule.subject_options.clear()
        rule.object_options.clear()
        for id in subject_option_ids:
            rule.subject_options.add(models.Option.objects.get(id = id))
        for id in object_option_ids:
            rule.object_options.add(models.Option.objects.get(id = id))
        rule.save()
    else:
        rule = models.Rule()
        rule.rule_type = models.RuleType.objects.get(id = int(type_id))
        rule.subject_question = question
        rule.object_question = models.Question.objects.get(id = object_question_id)
        rule.save()
        rule.object_options.clear()
        rule.subject_options.clear()
        for id in object_option_ids:
            rule.object_options.add(models.Option.objects.get(id = id))
        for id in subject_option_ids:
            rule.subject_options.add(models.Option.objects.get(id = id))
        rule.save()
    return rule
