# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'SiteSettings.contact_form_recipient'
        db.add_column('partnersites_sitesettings', 'contact_form_recipient', self.gf('django.db.models.fields.EmailField')(default=('Antwan Wiersma', 'webdev@grotegriepmeting.nl'), max_length=75, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'SiteSettings.contact_form_recipient'
        db.delete_column('partnersites_sitesettings', 'contact_form_recipient')


    models = {
        'partnersites.sitesettings': {
            'Meta': {'object_name': 'SiteSettings'},
            'contact_form_recipient': ('django.db.models.fields.EmailField', [], {'default': "('Antwan Wiersma', 'webdev@grotegriepmeting.nl')", 'max_length': '75', 'blank': 'True'}),
            'footer': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
