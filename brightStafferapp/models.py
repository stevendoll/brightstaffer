from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from time import time
from datetime import date
from django.db import models
from django.contrib.auth.models import User



# This code is triggered whenever a new user has been created and saved to the database
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Account(models.Model):
    client_id = models.IntegerField(verbose_name='Client ID', null=False, blank=False, primary_key=True)
    client_name = models.TextField(verbose_name='Client Name', null=False, blank=False)
    active=models.BooleanField(verbose_name='Active',default=True,null=False)
    domain_name=models.TextField(verbose_name='Domain Name', null=False, blank=False)
    account_manager=models.EmailField(verbose_name='Email ID', null=False, blank=False)
    def __unicode__(self):
        return self.client_id


class Projects(models.Model):
    project_id=models.IntegerField(verbose_name='Project ID', null=False, blank=False, primary_key=True)
    recuriter = models.ForeignKey(User,null=False, verbose_name='Recuriter ID')
    client = models.ForeignKey(Account,null=False, verbose_name='Client ID')
    title = models.TextField(verbose_name='Job Title', null=True, blank=True)
    description = models.TextField(verbose_name='Job Description', null=True, blank=True)
    industry = models.TextField(verbose_name='Industry', null=True, blank=True)
    functional = models.TextField(verbose_name='Functional', null=True, blank=True)
    minexp = models.IntegerField(verbose_name='Min Exp', null=True, blank=True)
    maxexp = models.IntegerField(verbose_name='Max Exp', null=True, blank=True)
    minsalary = models.FloatField(default=0.0,verbose_name='Min Salary', null=True, blank=True)
    maxsalary = models.FloatField(default=0.0,verbose_name='Max Salary', null=True, blank=True)
    location = models.TextField(verbose_name='Location', null=True, blank=True)
    jtype = models.CharField(max_length=20,verbose_name='Job Type', null=True, blank=True)
    qualification = models.TextField(verbose_name='Qualification', null=True, blank=True)

    def __unicode__(self):
        return self.email


def get_upload_file_name(instance, filename):
    return "uploaded_files/%s_%s" % (str(time()).replace('.', '_'), filename)

class Resume(models.Model):
    email = models.EmailField()
    resume = models.FileField(upload_to=get_upload_file_name)

    def __unicode__(self):
        return self.email

class Job_Posting(models.Model):
    email=models.EmailField()
    job_description=models.FileField(upload_to=get_upload_file_name)

    def __unicode__(self):
        return self.email


class Candidate(models.Model):
    candidate_id = models.IntegerField(verbose_name='Candidate ID', null=False, blank=False, primary_key=True)
    recuriter = models.ForeignKey(User,null=False, verbose_name='Recuriter ID')
    client = models.ForeignKey(Account,null=False, verbose_name='Client ID')
    email = models.EmailField(verbose_name='Candidate Email', null=False, blank=False)
    name = models.TextField(verbose_name='Candidate Name', null=False, blank=False)
    location = models.TextField(verbose_name='Location', null=True, blank=True)
    agree = models.CharField(max_length=5,verbose_name='Agree', null=True, blank=True)
    gender = models.CharField(max_length=6,verbose_name='Gender', null=False, blank=False)
    exp = models.IntegerField(default=0,verbose_name='Experience')
    title = models.TextField(verbose_name='Title', null=True, blank=True)
    company = models.TextField(verbose_name='Company Name', null=True, blank=True)
    skills = models.TextField(verbose_name='Skills', null=True, blank=True)
    sector = models.TextField(verbose_name='Sector', null=True, blank=True)
    functional = models.TextField(verbose_name='Functional', null=True, blank=True)
    minsalary = models.FloatField(default=0.0,verbose_name='Min Salary', null=True, blank=True)
    qualification = models.TextField(verbose_name='Qualification', null=True, blank=True)
    specialization = models.TextField(verbose_name='Specialization', null=True, blank=True)
    certification = models.TextField(verbose_name='Certification', null=True, blank=True)
    institute = models.TextField(verbose_name='Institute', null=True, blank=True)
    passing = models.IntegerField(default=1940,verbose_name='Passing', null=True, blank=True)
    jtype = models.TextField(verbose_name='Job type', null=True, blank=True)
    pubdate = models.DateField(default=date.today())

    def __unicode__(self):
        return self.email


class Project_Activity(models.Model):
    project_activity_id = models.IntegerField(verbose_name='Project Activity ID', null=False, blank=False, primary_key=True)
    project=models.ForeignKey(Projects,null=False,verbose_name='Project ID')
    recuriter=models.ForeignKey(User,null=False,verbose_name='Recuriter ID')
    candidate = models.IntegerField(verbose_name='Candidate ID', null=True, blank=True)
    action_type=models.TextField(verbose_name='Action Type', null=False, blank=False)
    date=models.DateField(verbose_name='Date', null=True, blank=True)
    details=models.TextField(verbose_name='Details', null=True, blank=True)
    summary=models.TextField(verbose_name='Summary', null=True, blank=True)
    def __unicode__(self):
        return self.project_activity_id

