# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-21 13:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='external_id',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
