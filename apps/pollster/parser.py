from django.db import models
from xml.etree import ElementTree
import re, warnings
import models

#########################
# decorated XHTML parsing
#########################

def survey_update_from_xhtml(survey, xmlstring):
    # ElementTree does not like being passed unicode objects
    xmlstring = '<?xml version="1.0" encoding="UTF-8"?>'+xmlstring.encode('utf-8')
    root = ElementTree.XML(xmlstring)

    survey.title = root.find('h1').text or ''
    survey.shortname = root.find('h1').get('data-shortname') or ''
    survey.version = root.find('h1').get('data-version') or ''
    survey.save()

    builtins = [q.data_name for q in survey.question_set.all() if q.is_builtin]
    if 'timestamp' not in builtins:
        question = models.Question()
        question.survey = survey
        question.data_name = 'timestamp'
        question.ordinal = 0
        question.type = 'builtin'
        question.title = 'Compilation Date'
        question.data_type = models.QuestionDataType.default_timestamp_type()
        question.save()

    idmap = {}
    question_ordinal = 1
    question_xrules = []
    for wrapper in root.findall('div'):
        if 'question-wrapper' not in wrapper.get('class'):
            continue
        xquestion = [i for i in wrapper if 'question' in i.get('class')][0]
        question = _update_question_from_xhtml(survey, idmap, xquestion, question_ordinal)
        question_ordinal += 1

        column_ordinal = 1
        xcolumns = [ul for ul in xquestion.findall('ul') if 'columns' in ul.get('class')] or [[]]
        for xcolumn in xcolumns[0]:
            _update_column_from_xhtml(survey, idmap, question, xcolumn, column_ordinal)
            column_ordinal += 1

        row_ordinal = 1
        xrows = [ul for ul in xquestion.findall('ul') if 'rows' in ul.get('class')] or [[]]
        for xrow in xrows[0]:
            _update_row_from_xhtml(survey, idmap, question, xrow, row_ordinal)
            row_ordinal += 1

        option_ordinal = 1
        xoptions = [ul for ul in xquestion.findall('ul') if 'choices' in ul.get('class') or 'derived-values' in ul.get('class')] or [[]]
        for xoption in xoptions[0]:
            _update_option_from_xhtml(survey, idmap, question, xoption, option_ordinal)
            option_ordinal += 1

        xrules = [i for i in wrapper if 'rules' in i.get('class')][0]
        question_xrules.append((question, xrules))

    # After generating correct IDs for all questions and options we process
    # the rules by iterating again the XML tree.

    for question, xrules in question_xrules:
        for xrule in xrules:
            _update_rule_from_xhtml(survey, idmap, question, xrule)

    survey.save()

def _get_question_id(idmap, idstr):
    return idmap[idstr]

def _get_option_id(idmap, idstr):
    return idmap[idstr]

def _update_question_from_xhtml(survey, idmap, root, ordinal):
    # Extract question ID and load corresponding question; if it does not exists
    # insert and empty question to generate it. In both cases we have a question
    # to fill with options and rules.
    question_type = root.get('data-question-type')
    data_type = root.get('data-data-type')
    open_option_data_type = root.get('data-open-option-data-type')
    visual = root.get('data-visual') or ''
    tags = root.get('data-tags')
    regex = None
    if root.find('input') is not None:
        regex = root.find('input').get('pattern')
    error_message = ([e.text for e in root.findall('p') if 'error-message' in e.get('class', '')] + [None]) [0]
    data_name = [e.text for e in root.findall('p/span') if 'data-name' in e.get('class', '')][0]
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

    if question_type == 'builtin':
        # builtin questions are not modifiable
        question = models.Question.objects.get(id = int(match.group(1)))
    elif deleted:
        models.Question.objects.filter(id = int(match.group(1))).exclude(type = 'builtin').delete()
        question = None
    elif match:
        question = models.Question.objects.get(id = int(match.group(1)))
        if question.type == 'builtin':
            raise StandardError('cannot modify builtin questions')
        question.data_name = data_name or ''
        question.title = title or ''
        question.description = description or ''
        question.tags = tags or ''
        question.regex = regex or ''
        question.error_message = error_message or ''
        question.starts_hidden = hidden
        question.is_mandatory = mandatory
        question.visual = visual
        question.ordinal = ordinal
        if data_type:
            question.data_type = models.QuestionDataType.objects.get(id = data_type)
        if open_option_data_type:
            question.open_option_data_type = models.QuestionDataType.objects.get(id = open_option_data_type)
        question.save()
    else:
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
        question.visual = visual
        question.ordinal = ordinal
        if data_type:
            question.data_type = models.QuestionDataType.objects.get(id = data_type)
        else:
            question.data_type = models.QuestionDataType.default_type()
        if open_option_data_type:
            question.open_option_data_type = models.QuestionDataType.objects.get(id = open_option_data_type)
        question.save()
    idmap[temp_id] = question and question.id
    return question

def _update_column_from_xhtml(survey, idmap, question, root, ordinal):
    temp_id = root.get('id') or ''
    match = re.match('^column-(\d+)$', temp_id)
    deleted = 'deleted' in (root.get('class') or '')
    if deleted or question is None:
        models.QuestionColumn.objects.filter(id = int(match.group(1))).delete()
        column = None
    else:
        title = [e.text for e in root.findall('span') if 'column-title' in e.get('class', '')][0]
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

def _update_row_from_xhtml(survey, idmap, question, root, ordinal):
    temp_id = root.get('id') or ''
    match = re.match('^row-(\d+)$', temp_id)
    deleted = 'deleted' in (root.get('class') or '')
    if deleted or question is None:
        models.QuestionRow.objects.filter(id = int(match.group(1))).delete()
        row = None
    else:
        title = [e.text for e in root.findall('span') if 'row-title' in e.get('class', '')][0]
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

def _update_option_from_xhtml(survey, idmap, question, root, ordinal):
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
        description = root.get('title')
        if match:
            option = models.Option.objects.get(id = int(match.group(1)))
            option.starts_hidden = hidden
            option.is_open = is_open
            option.text = text or ''
            option.value = value or ''
            option.description = description or ''
            option.ordinal = ordinal
            option.save()
        else:
            option = models.Option()
            option.question = question
            option.is_virtual = False
            option.starts_hidden = hidden
            option.is_open = is_open
            option.text = text or ''
            option.value = value or ''
            option.description = description or ''
            option.ordinal = ordinal
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
    idmap[temp_id] = option and option.id
    return option

def _update_rule_from_xhtml(survey, idmap, question, root):
    temp_id = root.get('id') or ''
    match = re.match('^rule-(\d+)$', temp_id)
    type_id = root.get('data-type')
    classes = root.get('class') or ''
    deleted = 'deleted' in classes
    is_sufficient = 'sufficient' in classes

    subject_option_ids = [_get_option_id(idmap, id) for id in root.get('data-subject-options', '').split()]
    subject_option_ids = [id for id in subject_option_ids if id is not None]
    object_question_id = root.get('data-object-question') and _get_question_id(idmap, root.get('data-object-question'))
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
        rule.is_sufficient = is_sufficient
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
        rule.is_sufficient = is_sufficient
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


#########################
# app-specific XML parsing
#########################

def get_ref(objects, element):
    if element is None:
        return None
    ref = element.get('ref')
    if not ref:
        return None
    if ref not in objects:
        raise KeyError("unable to resolve reference %s on element %s", ref, element.tag)
    return objects[ref]

def survey_update_from_xml(survey, xmlstring):
    # ElementTree does not like being passed unicode objects
    p = "{http://dndg.it/ns/pollster-1.0}" # pollster namespace
    xsurvey = ElementTree.XML(xmlstring)

    survey.title = xsurvey.findtext(p+'title')
    survey.shortname = xsurvey.findtext(p+'shortname')
    survey.version = xsurvey.findtext(p+'version')
    survey.save()

    questions = {}
    columns = {}
    rows = {}
    options = {}

    question_ordinal = 0
    for xquestion in xsurvey.find(p+'questions').findall(p+'question'):
        question_ordinal += 1
        question = models.Question()
        question.ordinal = question_ordinal
        question.survey = survey
        question.title = xquestion.findtext(p+'title')
        question.data_name = xquestion.findtext(p+'data_name')
        question.description = xquestion.findtext(p+'description')
        question.type = xquestion.findtext(p+'type')
        data_type = xquestion.findtext(p+'data_type')
        if data_type:
            question.data_type = models.QuestionDataType.objects.all().get(js_class=data_type)
        open_option_data_type = xquestion.findtext(p+'open_option_data_type')
        if open_option_data_type:
            question.open_option_data_type = models.QuestionDataType.objects.all().get(js_class=open_option_data_type)
        question.starts_hidden = xquestion.findtext(p+'starts_hidden').strip() == 'true'
        question.is_mandatory = xquestion.findtext(p+'is_mandatory').strip() == 'true'
        question.visual = xquestion.findtext(p+'visual')
        question.tags = xquestion.findtext(p+'tags')
        question.regex = xquestion.findtext(p+'regex')
        question.error_message = xquestion.findtext(p+'error_message')
        question.save()
        questions[xquestion.get('id')] = question

        column_ordinal = 0
        for xcolumn in xquestion.find(p+'columns').findall(p+'column'):
            column_ordinal += 1
            column = models.QuestionColumn()
            column.ordinal = column_ordinal
            column.question = question
            column.title = xcolumn.findtext(p+'title')
            column.save()
            columns[xcolumn.get('id')] = column

        row_ordinal = 0
        for xrow in xquestion.find(p+'rows').findall(p+'row'):
            row_ordinal += 1
            row = models.QuestionRow()
            row.ordinal = row_ordinal
            row.question = question
            row.title = xrow.findtext(p+'title')
            row.save()
            rows[xrow.get('id')] = row

        option_ordinal = 0
        for xoption in xquestion.find(p+'options').findall(p+'option'):
            option_ordinal += 1
            option = models.Option()
            option.ordinal = option_ordinal
            option.question = question
            option.column = get_ref(columns, xoption.find(p+'column'))
            option.row = get_ref(rows, xoption.find(p+'row'))
            option.group = xoption.findtext(p+'group')
            option.is_virtual = xoption.findtext(p+'is_virtual').strip() == 'true'
            virtual_type = xoption.findtext(p+'virtual_type')
            if virtual_type:
                option.virtual_type = models.VirtualOptionType.objects.all().get(js_class=virtual_type)
            option.virtual_inf = xoption.findtext(p+'virtual_inf') or ''
            option.virtual_sup = xoption.findtext(p+'virtual_sup') or ''
            option.virtual_regex = xoption.findtext(p+'virtual_regex') or ''
            option.text = xoption.findtext(p+'text') or ''
            option.value = xoption.findtext(p+'value') or ''
            option.is_open = (xoption.findtext(p+'is_open') or '').strip() == 'true'
            option.starts_hidden = (xoption.findtext(p+'starts_hidden') or '').strip() == 'true'
            option.save()
            options[xoption.get('id')] = option

    for xrule in xsurvey.find(p+'rules').findall(p+'rule'):
        rule = models.Rule()
        rule.is_sufficient = (xrule.findtext(p+'is_sufficient') or '').strip() == 'true'
        rule.rule_type = models.RuleType.objects.all().get(js_class=xrule.findtext(p+'type'))
        rule.subject_question = get_ref(questions, xrule.find(p+'subject_question'))
        rule.object_question = get_ref(questions, xrule.find(p+'object_question'))
        rule.save()
        xsubject_options = xrule.find(p+'subject_options').findall(p+'subject_option')
        rule.subject_options = [get_ref(options, x) for x in xsubject_options]
        xobject_options = xrule.find(p+'object_options').findall(p+'object_option')
        rule.object_options = [get_ref(options, x) for x in xobject_options]

    for xtranslation in xsurvey.find(p+'translations').findall(p+'translation'):
        translation = models.TranslationSurvey()
        translation.survey = survey
        translation.language = xtranslation.get('lang')
        translation.title = xtranslation.findtext(p+'title')
        translation.save()
        for xtquestion in xtranslation.find(p+'questions').findall(p+'question'):
            tquestion = models.TranslationQuestion()
            tquestion.translation = translation
            tquestion.question = get_ref(questions, xtquestion)
            tquestion.title = xtquestion.findtext(p+'title')
            tquestion.description = xtquestion.findtext(p+'description')
            tquestion.error_message = xtquestion.findtext(p+'error_message')
            tquestion.save()
        for xtcolumn in xtranslation.find(p+'columns').findall(p+'column'):
            tcolumn = models.TranslationQuestionColumn()
            tcolumn.translation = translation
            tcolumn.column = get_ref(columns, xtcolumn)
            tcolumn.title = xtcolumn.findtext(p+'title')
            tcolumn.save()
        for xtrow in xtranslation.find(p+'rows').findall(p+'row'):
            trow = models.TranslationQuestionRow()
            trow.translation = translation
            trow.row = get_ref(rows, xtrow)
            trow.title = xtrow.findtext(p+'title')
            trow.save()
        for xtoption in xtranslation.find(p+'options').findall(p+'option'):
            toption = models.TranslationOption()
            toption.translation = translation
            toption.option = get_ref(options, xtoption)
            toption.text = xtoption.findtext(p+'text')
            toption.save()
    return survey
