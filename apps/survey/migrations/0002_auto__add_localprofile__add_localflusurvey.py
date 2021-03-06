# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'LocalProfile'
        db.create_table('survey_localprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('surveyuser', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.SurveyUser'], unique=True)),
            ('sq_num_season', self.gf('django.db.models.fields.SmallIntegerField')(null=True)),
            ('sq_num_total', self.gf('django.db.models.fields.SmallIntegerField')(null=True)),
            ('sq_date_first', self.gf('django.db.models.fields.DateField')(null=True)),
            ('sq_date_last', self.gf('django.db.models.fields.DateField')(null=True)),
            ('birth_date', self.gf('django.db.models.fields.DateField')()),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('a_family', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('a_smoker', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('a_vaccine_prev_seasonal', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('a_vaccine_prev_swine', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('a_vaccine_current', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('survey', ['LocalProfile'])

        # Adding model 'LocalFluSurvey'
        db.create_table('survey_localflusurvey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('surveyuser', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.SurveyUser'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('age_user', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('survey_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('survey', ['LocalFluSurvey'])


    def backwards(self, orm):
        
        # Deleting model 'LocalProfile'
        db.delete_table('survey_localprofile')

        # Deleting model 'LocalFluSurvey'
        db.delete_table('survey_localflusurvey')


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
        'survey.localflusurvey': {
            'Meta': {'object_name': 'LocalFluSurvey'},
            'age_user': ('django.db.models.fields.SmallIntegerField', [], {}),
            'data': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'survey_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'surveyuser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.SurveyUser']"})
        },
        'survey.localprofile': {
            'Meta': {'object_name': 'LocalProfile'},
            'a_family': ('django.db.models.fields.SmallIntegerField', [], {}),
            'a_smoker': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'a_vaccine_current': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'a_vaccine_prev_seasonal': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'a_vaccine_prev_swine': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'birth_date': ('django.db.models.fields.DateField', [], {}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'sq_date_first': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'sq_date_last': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'sq_num_season': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'sq_num_total': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'surveyuser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.SurveyUser']", 'unique': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '5'})
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
            'global_id': ('django.db.models.fields.CharField', [], {'default': "'83aac21f-dc32-44d9-894d-54f72337a890'", 'unique': 'True', 'max_length': '36'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_participation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Participation']", 'null': 'True'}),
            'last_participation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['survey']
