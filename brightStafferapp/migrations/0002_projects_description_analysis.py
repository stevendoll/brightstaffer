# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-10 10:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brightStafferapp', '0001_brightstaffer_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='projects',
            name='description_analysis',
            field=models.TextField(blank=True, null=True, verbose_name='Job Description Analysis'),
        ),
    ]