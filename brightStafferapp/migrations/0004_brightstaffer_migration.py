# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-28 07:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brightStafferapp', '0003_0001_brightstaffer_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='projects',
            name='create_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='CreateDate'),
        ),
    ]
