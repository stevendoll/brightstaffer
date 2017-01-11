import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from time import time
from datetime import date
from django.db import models
from django.contrib.auth.models import User
import datetime


# This code is triggered whenever a new user has been created and saved to the database
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Projects(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recruiter = models.ForeignKey(User,null=False, verbose_name='Recruiter ID')
    project_name= models.CharField(max_length=255,verbose_name='Job Title', null=True, blank=True)
    company_name = models.CharField(max_length=255,verbose_name='Company Name', null=True, blank=True)
    location = models.CharField(max_length=255,verbose_name='Location', null=True, blank=True)
    description = models.TextField(verbose_name='Job Description', null=True, blank=True)
    is_published=models.TextField(verbose_name='Published',default=False,null=False)
    create_date=models.DateTimeField(verbose_name='CreateDate',null=True, blank=True)
    description_analysis=models.TextField(verbose_name='Job Description Analysis', null=True, blank=True)
    class Meta:
        verbose_name_plural = 'Projects'
        verbose_name = 'Projects'
        db_table = 'projects'

    def __str__(self):
        return str(self.id)



class Concept(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Projects, null=False, verbose_name='Project ID')
    concept=models.TextField(verbose_name='Job Concept',null=True, blank=True)
    class Meta:
        verbose_name_plural = 'Concepts'
        verbose_name = 'Concept'
        db_table = 'concepts'

    def __int__(self):
        return str(self.id)

def get_upload_file_name(instance, filename):
    return "uploaded_files/%s_%s" % (str(time()).replace('.', '_'), filename)

