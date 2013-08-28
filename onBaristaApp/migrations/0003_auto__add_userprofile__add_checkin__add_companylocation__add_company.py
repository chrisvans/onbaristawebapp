# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table(u'onBaristaApp_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('mug', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('isCompanyAdmin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('full_name', self.gf('django.db.models.fields.CharField')(default='', max_length=50, null=True, blank=True)),
            ('userType', self.gf('django.db.models.fields.CharField')(default='Consumer', max_length=10)),
            ('favCompany', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['onBaristaApp.Company'], null=True, blank=True)),
            ('favBaristaObj', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['onBaristaApp.UserProfile'], null=True, blank=True)),
            ('usercheckedin', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'onBaristaApp', ['UserProfile'])

        # Adding model 'checkIn'
        db.create_table(u'onBaristaApp_checkin', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('barista', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['onBaristaApp.companyLocation'])),
            ('inTime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('outTime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('checkedin', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'onBaristaApp', ['checkIn'])

        # Adding model 'companyLocation'
        db.create_table(u'onBaristaApp_companylocation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('companyID', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['onBaristaApp.Company'])),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='MA', max_length=2, blank=True)),
            ('zipCode', self.gf('django.db.models.fields.CharField')(max_length=5, blank=True)),
        ))
        db.send_create_signal(u'onBaristaApp', ['companyLocation'])

        # Adding model 'Company'
        db.create_table(u'onBaristaApp_company', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('companyName', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('companyContact', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'onBaristaApp', ['Company'])


    def backwards(self, orm):
        # Deleting model 'UserProfile'
        db.delete_table(u'onBaristaApp_userprofile')

        # Deleting model 'checkIn'
        db.delete_table(u'onBaristaApp_checkin')

        # Deleting model 'companyLocation'
        db.delete_table(u'onBaristaApp_companylocation')

        # Deleting model 'Company'
        db.delete_table(u'onBaristaApp_company')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'onBaristaApp.checkin': {
            'Meta': {'object_name': 'checkIn'},
            'barista': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'checkedin': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inTime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['onBaristaApp.companyLocation']"}),
            'outTime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        u'onBaristaApp.company': {
            'Meta': {'object_name': 'Company'},
            'companyContact': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'companyName': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'onBaristaApp.companylocation': {
            'Meta': {'object_name': 'companyLocation'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'companyID': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['onBaristaApp.Company']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'MA'", 'max_length': '2', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'zipCode': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'})
        },
        u'onBaristaApp.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'favBaristaObj': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['onBaristaApp.UserProfile']", 'null': 'True', 'blank': 'True'}),
            'favCompany': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['onBaristaApp.Company']", 'null': 'True', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isCompanyAdmin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mug': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'userType': ('django.db.models.fields.CharField', [], {'default': "'Consumer'", 'max_length': '10'}),
            'usercheckedin': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['onBaristaApp']