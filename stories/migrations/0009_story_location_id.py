# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-02 15:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0008_add_keyword_to_story'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='location_id',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
