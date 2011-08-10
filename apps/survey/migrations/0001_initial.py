# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SurveyUser'
        db.create_table('survey_surveyuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('global_id', self.gf('django.db.models.fields.CharField')(default='624d10b6-bde5-438f-81d9-862d43b58a17', unique=True, max_length=36)),
            ('last_participation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Participation'], null=True)),
            ('last_participation_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('survey', ['SurveyUser'])

        # Adding M2M table for field user on 'SurveyUser'
        db.create_table('survey_surveyuser_user', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('surveyuser', models.ForeignKey(orm['survey.surveyuser'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('survey_surveyuser_user', ['surveyuser_id', 'user_id'])

        # Adding model 'Survey'
        db.create_table('survey_survey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('specification', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('survey', ['Survey'])

        # Adding model 'Participation'
        db.create_table('survey_participation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.SurveyUser'])),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Survey'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('epidb_id', self.gf('django.db.models.fields.CharField')(max_length=36, null=True)),
            ('previous_participation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Participation'], null=True)),
            ('previous_participation_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('survey', ['Participation'])

        # Adding model 'ResponseSendQueue'
        db.create_table('survey_responsesendqueue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('participation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Participation'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('survey_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('answers', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('survey', ['ResponseSendQueue'])

        # Adding model 'ProfileSendQueue'
        db.create_table('survey_profilesendqueue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.SurveyUser'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('survey_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('answers', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('survey', ['ProfileSendQueue'])

        # Adding model 'LocalResponse'
        db.create_table('survey_localresponse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('survey_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('answers', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('survey', ['LocalResponse'])

        # Adding model 'Profile'
        db.create_table('survey_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.SurveyUser'], unique=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('data', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['survey.Survey'], null=True)),
        ))
        db.send_create_signal('survey', ['Profile'])

        # Adding model 'LastResponse'
        db.create_table('survey_lastresponse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.SurveyUser'], unique=True)),
            ('participation', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['survey.Participation'], null=True)),
            ('data', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('survey', ['LastResponse'])

        # Adding model 'ExtraResponse'
        db.create_table('survey_extraresponse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.SurveyUser'])),
            ('participation', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['survey.Participation'], null=True)),
            ('data', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('survey', ['ExtraResponse'])


    def backwards(self, orm):
        
        # Deleting model 'SurveyUser'
        db.delete_table('survey_surveyuser')

        # Removing M2M table for field user on 'SurveyUser'
        db.delete_table('survey_surveyuser_user')

        # Deleting model 'Survey'
        db.delete_table('survey_survey')

        # Deleting model 'Participation'
        db.delete_table('survey_participation')

        # Deleting model 'ResponseSendQueue'
        db.delete_table('survey_responsesendqueue')

        # Deleting model 'ProfileSendQueue'
        db.delete_table('survey_profilesendqueue')

        # Deleting model 'LocalResponse'
        db.delete_table('survey_localresponse')

        # Deleting model 'Profile'
        db.delete_table('survey_profile')

        # Deleting model 'LastResponse'
        db.delete_table('survey_lastresponse')

        # Deleting model 'ExtraResponse'
        db.delete_table('survey_extraresponse')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'survey.extraresponse': {
            'Meta': {'object_name': 'ExtraResponse'},
            'data': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participation': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['survey.Participation']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.SurveyUser']"})
        },
        'survey.lastresponse': {
            'Meta': {'object_name': 'LastResponse'},
            'data': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participation': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['survey.Participation']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.SurveyUser']", 'unique': 'True'})
        },
        'survey.localresponse': {
            'Meta': {'object_name': 'LocalResponse'},
            'answers': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'survey_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '36'})
        },
        'survey.participation': {
            'Meta': {'object_name': 'Participation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'epidb_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'previous_participation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Participation']", 'null': 'True'}),
            'previous_participation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Survey']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.SurveyUser']"})
        },
        'survey.profile': {
            'Meta': {'object_name': 'Profile'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['survey.Survey']", 'null': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.SurveyUser']", 'unique': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'survey.profilesendqueue': {
            'Meta': {'object_name': 'ProfileSendQueue'},
            'answers': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.SurveyUser']"}),
            'survey_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '36'})
        },
        'survey.responsesendqueue': {
            'Meta': {'object_name': 'ResponseSendQueue'},
            'answers': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Participation']"}),
            'survey_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '36'})
        },
        'survey.survey': {
            'Meta': {'object_name': 'Survey'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'specification': ('django.db.models.fields.TextField', [], {}),
            'survey_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'survey.surveyuser': {
            'Meta': {'object_name': 'SurveyUser'},
            'global_id': ('django.db.models.fields.CharField', [], {'default': "'b56bab47-c416-424d-8ac5-fe250560681e'", 'unique': 'True', 'max_length': '36'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_participation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Participation']", 'null': 'True'}),
            'last_participation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['survey']
