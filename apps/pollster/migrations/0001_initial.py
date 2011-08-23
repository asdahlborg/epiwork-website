# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Survey'
        db.create_table('pollster_survey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.Survey'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('shortname', self.gf('django.db.models.fields.SlugField')(default='', max_length=255, db_index=True)),
            ('version', self.gf('django.db.models.fields.SlugField')(default='', max_length=255, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='DRAFT', max_length=255)),
        ))
        db.send_create_signal('pollster', ['Survey'])

        # Adding model 'RuleType'
        db.create_table('pollster_ruletype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('js_class', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('pollster', ['RuleType'])

        # Adding model 'QuestionDataType'
        db.create_table('pollster_questiondatatype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('db_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('css_class', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('js_class', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('pollster', ['QuestionDataType'])

        # Adding model 'VirtualOptionType'
        db.create_table('pollster_virtualoptiontype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('question_data_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.QuestionDataType'])),
            ('js_class', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('pollster', ['VirtualOptionType'])

        # Adding model 'Question'
        db.create_table('pollster_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.Survey'])),
            ('starts_hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_mandatory', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ordinal', self.gf('django.db.models.fields.IntegerField')()),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('data_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.QuestionDataType'])),
            ('open_option_data_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='questions_with_open_option', null=True, to=orm['pollster.QuestionDataType'])),
            ('data_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('visual', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('tags', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('regex', self.gf('django.db.models.fields.CharField')(default='', max_length=1023, blank=True)),
            ('error_message', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('pollster', ['Question'])

        # Adding model 'QuestionRow'
        db.create_table('pollster_questionrow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='row_set', to=orm['pollster.Question'])),
            ('ordinal', self.gf('django.db.models.fields.IntegerField')()),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
        ))
        db.send_create_signal('pollster', ['QuestionRow'])

        # Adding model 'QuestionColumn'
        db.create_table('pollster_questioncolumn', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='column_set', to=orm['pollster.Question'])),
            ('ordinal', self.gf('django.db.models.fields.IntegerField')()),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
        ))
        db.send_create_signal('pollster', ['QuestionColumn'])

        # Adding model 'Option'
        db.create_table('pollster_option', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.Question'])),
            ('clone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.Option'], null=True, blank=True)),
            ('row', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.QuestionRow'], null=True, blank=True)),
            ('column', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.QuestionColumn'], null=True, blank=True)),
            ('is_virtual', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_open', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('starts_hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ordinal', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('text', self.gf('django.db.models.fields.CharField')(default='', max_length=4095, blank=True)),
            ('group', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('value', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('virtual_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.VirtualOptionType'], null=True, blank=True)),
            ('virtual_inf', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('virtual_sup', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('virtual_regex', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
        ))
        db.send_create_signal('pollster', ['Option'])

        # Adding model 'Rule'
        db.create_table('pollster_rule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rule_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.RuleType'])),
            ('subject_question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='subject_of_rules', to=orm['pollster.Question'])),
            ('object_question', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='object_of_rules', null=True, to=orm['pollster.Question'])),
        ))
        db.send_create_signal('pollster', ['Rule'])

        # Adding M2M table for field subject_options on 'Rule'
        db.create_table('pollster_rule_subject_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rule', models.ForeignKey(orm['pollster.rule'], null=False)),
            ('option', models.ForeignKey(orm['pollster.option'], null=False))
        ))
        db.create_unique('pollster_rule_subject_options', ['rule_id', 'option_id'])

        # Adding M2M table for field object_options on 'Rule'
        db.create_table('pollster_rule_object_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rule', models.ForeignKey(orm['pollster.rule'], null=False)),
            ('option', models.ForeignKey(orm['pollster.option'], null=False))
        ))
        db.create_unique('pollster_rule_object_options', ['rule_id', 'option_id'])

        # Adding model 'TranslationSurvey'
        db.create_table('pollster_translationsurvey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.Survey'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=3, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='DRAFT', max_length=255)),
        ))
        db.send_create_signal('pollster', ['TranslationSurvey'])

        # Adding unique constraint on 'TranslationSurvey', fields ['survey', 'language']
        db.create_unique('pollster_translationsurvey', ['survey_id', 'language'])

        # Adding model 'TranslationQuestion'
        db.create_table('pollster_translationquestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('translation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.TranslationSurvey'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.Question'])),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('error_message', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('pollster', ['TranslationQuestion'])

        # Adding unique constraint on 'TranslationQuestion', fields ['translation', 'question']
        db.create_unique('pollster_translationquestion', ['translation_id', 'question_id'])

        # Adding model 'TranslationQuestionRow'
        db.create_table('pollster_translationquestionrow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('translation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.TranslationSurvey'])),
            ('row', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.QuestionRow'])),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
        ))
        db.send_create_signal('pollster', ['TranslationQuestionRow'])

        # Adding unique constraint on 'TranslationQuestionRow', fields ['translation', 'row']
        db.create_unique('pollster_translationquestionrow', ['translation_id', 'row_id'])

        # Adding model 'TranslationQuestionColumn'
        db.create_table('pollster_translationquestioncolumn', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('translation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.TranslationSurvey'])),
            ('column', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.QuestionColumn'])),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
        ))
        db.send_create_signal('pollster', ['TranslationQuestionColumn'])

        # Adding unique constraint on 'TranslationQuestionColumn', fields ['translation', 'column']
        db.create_unique('pollster_translationquestioncolumn', ['translation_id', 'column_id'])

        # Adding model 'TranslationOption'
        db.create_table('pollster_translationoption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('translation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.TranslationSurvey'])),
            ('option', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.Option'])),
            ('text', self.gf('django.db.models.fields.CharField')(default='', max_length=4095, blank=True)),
        ))
        db.send_create_signal('pollster', ['TranslationOption'])

        # Adding unique constraint on 'TranslationOption', fields ['translation', 'option']
        db.create_unique('pollster_translationoption', ['translation_id', 'option_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'TranslationOption', fields ['translation', 'option']
        db.delete_unique('pollster_translationoption', ['translation_id', 'option_id'])

        # Removing unique constraint on 'TranslationQuestionColumn', fields ['translation', 'column']
        db.delete_unique('pollster_translationquestioncolumn', ['translation_id', 'column_id'])

        # Removing unique constraint on 'TranslationQuestionRow', fields ['translation', 'row']
        db.delete_unique('pollster_translationquestionrow', ['translation_id', 'row_id'])

        # Removing unique constraint on 'TranslationQuestion', fields ['translation', 'question']
        db.delete_unique('pollster_translationquestion', ['translation_id', 'question_id'])

        # Removing unique constraint on 'TranslationSurvey', fields ['survey', 'language']
        db.delete_unique('pollster_translationsurvey', ['survey_id', 'language'])

        # Deleting model 'Survey'
        db.delete_table('pollster_survey')

        # Deleting model 'RuleType'
        db.delete_table('pollster_ruletype')

        # Deleting model 'QuestionDataType'
        db.delete_table('pollster_questiondatatype')

        # Deleting model 'VirtualOptionType'
        db.delete_table('pollster_virtualoptiontype')

        # Deleting model 'Question'
        db.delete_table('pollster_question')

        # Deleting model 'QuestionRow'
        db.delete_table('pollster_questionrow')

        # Deleting model 'QuestionColumn'
        db.delete_table('pollster_questioncolumn')

        # Deleting model 'Option'
        db.delete_table('pollster_option')

        # Deleting model 'Rule'
        db.delete_table('pollster_rule')

        # Removing M2M table for field subject_options on 'Rule'
        db.delete_table('pollster_rule_subject_options')

        # Removing M2M table for field object_options on 'Rule'
        db.delete_table('pollster_rule_object_options')

        # Deleting model 'TranslationSurvey'
        db.delete_table('pollster_translationsurvey')

        # Deleting model 'TranslationQuestion'
        db.delete_table('pollster_translationquestion')

        # Deleting model 'TranslationQuestionRow'
        db.delete_table('pollster_translationquestionrow')

        # Deleting model 'TranslationQuestionColumn'
        db.delete_table('pollster_translationquestioncolumn')

        # Deleting model 'TranslationOption'
        db.delete_table('pollster_translationoption')


    models = {
        'pollster.option': {
            'Meta': {'ordering': "['question', 'ordinal']", 'object_name': 'Option'},
            'clone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Option']", 'null': 'True', 'blank': 'True'}),
            'column': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionColumn']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_virtual': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Question']"}),
            'row': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionRow']", 'null': 'True', 'blank': 'True'}),
            'starts_hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4095', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'virtual_inf': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'virtual_regex': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'virtual_sup': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'virtual_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.VirtualOptionType']", 'null': 'True', 'blank': 'True'})
        },
        'pollster.question': {
            'Meta': {'ordering': "['survey', 'ordinal']", 'object_name': 'Question'},
            'data_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionDataType']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'error_message': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_mandatory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'open_option_data_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'questions_with_open_option'", 'null': 'True', 'to': "orm['pollster.QuestionDataType']"}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'regex': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1023', 'blank': 'True'}),
            'starts_hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Survey']"}),
            'tags': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'visual': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.questioncolumn': {
            'Meta': {'ordering': "['question', 'ordinal']", 'object_name': 'QuestionColumn'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'column_set'", 'to': "orm['pollster.Question']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.questiondatatype': {
            'Meta': {'object_name': 'QuestionDataType'},
            'css_class': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'db_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'js_class': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.questionrow': {
            'Meta': {'ordering': "['question', 'ordinal']", 'object_name': 'QuestionRow'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'row_set'", 'to': "orm['pollster.Question']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.rule': {
            'Meta': {'object_name': 'Rule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_options': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'object_of_rules'", 'symmetrical': 'False', 'to': "orm['pollster.Option']"}),
            'object_question': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'object_of_rules'", 'null': 'True', 'to': "orm['pollster.Question']"}),
            'rule_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.RuleType']"}),
            'subject_options': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'subject_of_rules'", 'symmetrical': 'False', 'to': "orm['pollster.Option']"}),
            'subject_question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subject_of_rules'", 'to': "orm['pollster.Question']"})
        },
        'pollster.ruletype': {
            'Meta': {'object_name': 'RuleType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'js_class': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.survey': {
            'Meta': {'object_name': 'Survey'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Survey']", 'null': 'True', 'blank': 'True'}),
            'shortname': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '255', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'DRAFT'", 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '255', 'db_index': 'True'})
        },
        'pollster.translationoption': {
            'Meta': {'ordering': "['translation', 'option']", 'unique_together': "(('translation', 'option'),)", 'object_name': 'TranslationOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Option']"}),
            'text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4095', 'blank': 'True'}),
            'translation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.TranslationSurvey']"})
        },
        'pollster.translationquestion': {
            'Meta': {'ordering': "['translation', 'question']", 'unique_together': "(('translation', 'question'),)", 'object_name': 'TranslationQuestion'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'error_message': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Question']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'translation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.TranslationSurvey']"})
        },
        'pollster.translationquestioncolumn': {
            'Meta': {'ordering': "['translation', 'column']", 'unique_together': "(('translation', 'column'),)", 'object_name': 'TranslationQuestionColumn'},
            'column': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionColumn']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'translation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.TranslationSurvey']"})
        },
        'pollster.translationquestionrow': {
            'Meta': {'ordering': "['translation', 'row']", 'unique_together': "(('translation', 'row'),)", 'object_name': 'TranslationQuestionRow'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionRow']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'translation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.TranslationSurvey']"})
        },
        'pollster.translationsurvey': {
            'Meta': {'ordering': "['survey', 'language']", 'unique_together': "(('survey', 'language'),)", 'object_name': 'TranslationSurvey'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'DRAFT'", 'max_length': '255'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Survey']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.virtualoptiontype': {
            'Meta': {'object_name': 'VirtualOptionType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'js_class': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'question_data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionDataType']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['pollster']
