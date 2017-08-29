# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-29 12:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0017_add_activity_streams_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='KeywordTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='Name')),
            ],
            options={
                'managed': True,
                'default_permissions': (),
                'verbose_name': 'Keyword Translation',
                'db_table': 'stories_keyword_translation',
                'db_tablespace': '',
            },
        ),
        migrations.RenameField(
            model_name='keyword',
            old_name='yso',
            new_name='external_id',
        ),
        migrations.AddField(
            model_name='keywordtranslation',
            name='master',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='stories.Keyword'),
        ),
        migrations.AlterUniqueTogether(
            name='keywordtranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
