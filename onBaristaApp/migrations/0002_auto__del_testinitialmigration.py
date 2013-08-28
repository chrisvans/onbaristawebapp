# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'TestInitialMigration'
        db.delete_table(u'onBaristaApp_testinitialmigration')


    def backwards(self, orm):
        # Adding model 'TestInitialMigration'
        db.create_table(u'onBaristaApp_testinitialmigration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'onBaristaApp', ['TestInitialMigration'])


    models = {
        
    }

    complete_apps = ['onBaristaApp']