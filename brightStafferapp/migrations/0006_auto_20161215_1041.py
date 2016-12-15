# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-15 10:41
from __future__ import unicode_literals

import brightStafferapp.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('brightStafferapp', '0005_delete_user_signup'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('client_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='Client ID')),
                ('client_name', models.TextField(verbose_name='Client Name')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('domain_name', models.TextField(verbose_name='Domain Name')),
                ('account_manager', models.EmailField(max_length=254, verbose_name='Email ID')),
            ],
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('candidate_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='Candidate ID')),
                ('email', models.EmailField(max_length=254, verbose_name='Candidate Email')),
                ('name', models.TextField(verbose_name='Candidate Name')),
                ('location', models.TextField(blank=True, null=True, verbose_name='Location')),
                ('agree', models.CharField(blank=True, max_length=5, null=True, verbose_name='Agree')),
                ('gender', models.CharField(max_length=6, verbose_name='Gender')),
                ('exp', models.IntegerField(default=0, verbose_name='Experience')),
                ('title', models.TextField(blank=True, null=True, verbose_name='Title')),
                ('company', models.TextField(blank=True, null=True, verbose_name='Company Name')),
                ('skills', models.TextField(blank=True, null=True, verbose_name='Skills')),
                ('sector', models.TextField(blank=True, null=True, verbose_name='Sector')),
                ('functional', models.TextField(blank=True, null=True, verbose_name='Functional')),
                ('minsalary', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Min Salary')),
                ('qualification', models.TextField(blank=True, null=True, verbose_name='Qualification')),
                ('specialization', models.TextField(blank=True, null=True, verbose_name='Specialization')),
                ('certification', models.TextField(blank=True, null=True, verbose_name='Certification')),
                ('institute', models.TextField(blank=True, null=True, verbose_name='Institute')),
                ('passing', models.IntegerField(blank=True, default=1940, null=True, verbose_name='Passing')),
                ('jtype', models.TextField(blank=True, null=True, verbose_name='Job type')),
                ('pubdate', models.DateField(default=datetime.date(2016, 12, 15))),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brightStafferapp.Account', verbose_name='Client ID')),
                ('recuriter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Recuriter ID')),
            ],
        ),
        migrations.CreateModel(
            name='Job_Posting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('job_description', models.FileField(upload_to=brightStafferapp.models.get_upload_file_name)),
            ],
        ),
        migrations.CreateModel(
            name='Project_Activity',
            fields=[
                ('project_activity_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='Project Activity ID')),
                ('candidate', models.IntegerField(blank=True, null=True, verbose_name='Candidate ID')),
                ('action_type', models.TextField(verbose_name='Action Type')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Date')),
                ('details', models.TextField(blank=True, null=True, verbose_name='Details')),
                ('summary', models.TextField(blank=True, null=True, verbose_name='Summary')),
            ],
        ),
        migrations.CreateModel(
            name='Projects',
            fields=[
                ('project_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='Project ID')),
                ('title', models.TextField(blank=True, null=True, verbose_name='Job Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Job Description')),
                ('industry', models.TextField(blank=True, null=True, verbose_name='Industry')),
                ('functional', models.TextField(blank=True, null=True, verbose_name='Functional')),
                ('minexp', models.IntegerField(blank=True, null=True, verbose_name='Min Exp')),
                ('maxexp', models.IntegerField(blank=True, null=True, verbose_name='Max Exp')),
                ('minsalary', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Min Salary')),
                ('maxsalary', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Max Salary')),
                ('location', models.TextField(blank=True, null=True, verbose_name='Location')),
                ('jtype', models.CharField(blank=True, max_length=20, null=True, verbose_name='Job Type')),
                ('qualification', models.TextField(blank=True, null=True, verbose_name='Qualification')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brightStafferapp.Account', verbose_name='Client ID')),
                ('recuriter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Recuriter ID')),
            ],
        ),
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('resume', models.FileField(upload_to=brightStafferapp.models.get_upload_file_name)),
            ],
        ),
        migrations.AddField(
            model_name='project_activity',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brightStafferapp.Projects', verbose_name='Project ID'),
        ),
        migrations.AddField(
            model_name='project_activity',
            name='recuriter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Recuriter ID'),
        ),
    ]
