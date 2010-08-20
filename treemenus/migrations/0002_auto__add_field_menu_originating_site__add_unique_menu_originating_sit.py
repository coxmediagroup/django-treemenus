# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Menu.originating_site'
        db.add_column('treemenus_menu', 'originating_site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'], null=True, blank=True), keep_default=False)

        # Adding M2M table for field sites on 'Menu'
        db.create_table('treemenus_menu_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('menu', models.ForeignKey(orm['treemenus.menu'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('treemenus_menu_sites', ['menu_id', 'site_id'])

        # Adding unique constraint on 'Menu', fields ['originating_site', 'name']
        db.create_unique('treemenus_menu', ['originating_site_id', 'name'])


    def backwards(self, orm):
        
        # Deleting field 'Menu.originating_site'
        db.delete_column('treemenus_menu', 'originating_site_id')

        # Removing M2M table for field sites on 'Menu'
        db.delete_table('treemenus_menu_sites')

        # Removing unique constraint on 'Menu', fields ['originating_site', 'name']
        db.delete_unique('treemenus_menu', ['originating_site_id', 'name'])


    models = {
        'sites.site': {
            'Meta': {'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'treemenus.menu': {
            'Meta': {'unique_together': "(('originating_site', 'name'),)", 'object_name': 'Menu'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'originating_site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']", 'null': 'True', 'blank': 'True'}),
            'root_item': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'is_root_item_of'", 'null': 'True', 'to': "orm['treemenus.MenuItem']"}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treemenus_menu_sites'", 'symmetrical': 'False', 'to': "orm['sites.Site']"})
        },
        'treemenus.menuitem': {
            'Meta': {'object_name': 'MenuItem'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'menu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contained_items'", 'null': 'True', 'to': "orm['treemenus.Menu']"}),
            'named_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['treemenus.MenuItem']", 'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['treemenus']
