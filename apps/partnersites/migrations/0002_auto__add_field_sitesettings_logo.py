# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'SiteSettings.logo'
        db.add_column('partnersites_sitesettings', 'logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'SiteSettings.logo'
        db.delete_column('partnersites_sitesettings', 'logo')


    models = {
        'partnersites.sitesettings': {
            'Meta': {'object_name': 'SiteSettings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'light_color': ('django.db.models.fields.CharField', [], {'default': "'ce2626'", 'max_length': '6'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
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
