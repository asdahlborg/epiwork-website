# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SiteSettings'
        db.create_table('partnersites_sitesettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sites.Site'], unique=True)),
            ('light_color', self.gf('django.db.models.fields.CharField')(max_length=6)),
        ))
        db.send_create_signal('partnersites', ['SiteSettings'])


    def backwards(self, orm):
        
        # Deleting model 'SiteSettings'
        db.delete_table('partnersites_sitesettings')


    models = {
        'partnersites.sitesettings': {
            'Meta': {'object_name': 'SiteSettings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'light_color': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sites.Site']", 'unique': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['partnersites']
