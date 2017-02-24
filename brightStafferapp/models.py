import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from time import time
from django.db import models
from django.contrib.auth.models import User


# This code is triggered whenever a new user has been created and saved to the database
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Projects(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recruiter = models.ForeignKey(User, null=False, verbose_name='Recruiter ID')
    project_name = models.CharField(max_length=255, verbose_name='Job Title', null=True, blank=True)
    company_name = models.CharField(max_length=255, verbose_name='Company Name', null=True, blank=True)
    location = models.CharField(max_length=255, verbose_name='Location', null=True, blank=True)
    description = models.TextField(verbose_name='Job Description', null=True, blank=True)
    is_published = models.BooleanField(verbose_name='Published', default=False, null=False)
    create_date = models.DateTimeField(verbose_name='CreateDate', null=True, blank=True)
    description_analysis = models.TextField(verbose_name='Job Description Analysis', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Projects'
        verbose_name = 'Projects'
        db_table = 'projects'

    def __str__(self):
        return str(self.id)

    @property
    def get_date(self):
        return self.create_date.date().strftime('%d/%m/%Y')


class Concept(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Projects, null=False, verbose_name='Project ID', related_name="concepts")
    concept = models.TextField(verbose_name='Job Concept',null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Concepts'
        verbose_name = 'Concept'
        db_table = 'concepts'

    def __int__(self):
        return str(self.id)

    def __str__(self):
        return str(self.concept)


def get_upload_file_name(instance, filename):
    return "uploaded_files/%s_%s" % (str(time()).replace('.', '_'), filename)


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=255, verbose_name='Company Name', null=True, blank=True)
    location = models.CharField(max_length=100, default='')

    class Meta:
        verbose_name_plural = 'Company'
        verbose_name = 'Company'
        db_table = 'company'

    def __str__(self):
        return str(self.company_name)


class Talent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    talent_name = models.CharField(max_length=100, verbose_name='Talent Name', null=False, blank=False,
                                   default='')
    company = models.ManyToManyField(Company)
    recruiter = models.ForeignKey(User, null=False, verbose_name='Recruiter ID')
    project = models.ForeignKey(Projects, null=True, verbose_name='Project Name')
    current_location = models.CharField(max_length=255, verbose_name='Current Location', null=True, blank=True)
    create_date = models.DateTimeField(verbose_name='CreateDate', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Talent'
        verbose_name = 'Talent'
        db_table = 'talent'

    def __str__(self):
        return str(self.talent_name)

    @property
    def get_date(self):
        return self.create_date.date().strftime('%d/%m/%Y')


class TalentCompany(models.Model):
    talent = models.ForeignKey(Talent, null=False, blank=True, verbose_name='Talent')
    company = models.ForeignKey(Company, null=False, blank=True, verbose_name='Company')
    start_date = models.DateField(verbose_name='Start Date', null=True, blank=True)
    end_date = models.DateField(verbose_name='End Date', null=True, blank=True)
    is_current = models.BooleanField(verbose_name='Currently Working Here', default=False, null=False)

    class Meta:

        db_table = 'talent_company_tb'

    def __str__(self):
        return str(self.talent.talent_name + " works at " + self.company.company_name)