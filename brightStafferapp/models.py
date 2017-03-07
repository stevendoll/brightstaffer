import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from time import time
from django.db import models
from django.contrib.auth.models import User
import PyPDF2
from PIL import Image
import os
import uuid
import textract


STAGE_CHOICES = (('Contacted', 'Contacted'),
                 ('Replied', 'Replied'),
                 ('Interested', 'Interested'),
                 ('Not Interested', 'Not Interested'),
                 ('Under Review', 'Under Review'),
                 ('Scheduled For Interview', 'Scheduled For Interview'),
                 ('Interviewing', 'Interviewing'),
                 ('Offer', 'Offer'),
                 ('Hired', 'Hired'),
                 ('Rejected', 'Rejected')
                 )

TALENT_CHOICES = (('New', 'New'),
                  ('Active', 'Active')
                  )


# This code is triggered whenever a new user has been created and saved to the database
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_recruiter_object(sender, instance=None, created=False, **kwargs):
    if created:
        dp_name = instance.first_name + " " + instance.last_name
        Recruiter.objects.create(user=instance, display_name=dp_name)


class Recruiter(models.Model):
    user = models.OneToOneField(User, related_name='user_recruiter')
    display_name = models.CharField(max_length=100, null=True, blank=True)


class Concept(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    concept = models.CharField(max_length=100, default='')
    date_created = models.DateField(auto_now_add=True, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'concepts'

    def __str__(self):
        return self.concept


class Projects(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recruiter = models.ForeignKey(User, null=False, verbose_name='Recruiter ID')
    project_name = models.CharField(max_length=255, verbose_name='Job Title', null=True, blank=True)
    company_name = models.CharField(max_length=255, verbose_name='Company Name', null=True, blank=True)
    location = models.CharField(max_length=255, verbose_name='Location', null=True, blank=True)
    concepts = models.ManyToManyField(Concept, through='ProjectConcept')
    description = models.TextField(verbose_name='Job Description', null=True, blank=True)
    is_published = models.BooleanField(verbose_name='Published', default=False, null=False)
    create_date = models.DateTimeField(verbose_name='CreateDate', null=True, blank=True)
    description_analysis = models.TextField(verbose_name='Job Description Analysis', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Projects'
        verbose_name = 'Projects'
        db_table = 'projects'

    def __str__(self):
        return str(self.project_name)

    @property
    def get_date(self):
        return self.create_date.date().strftime('%d/%m/%Y')


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


class Education(models.Model):
    name = models.CharField(max_length=250, verbose_name="Institution Name")
    location = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Talent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    talent_name = models.CharField(max_length=100, verbose_name='Talent Name', null=False, blank=False,
                                   default='')
    designation = models.CharField(max_length=100, default='', null=True, blank=True)
    industry_focus = models.CharField(max_length=100, default='', null=True, blank=True)
    industry_focus_percentage = models.CharField(max_length=30, default='', null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True, max_length=300)
    company = models.ManyToManyField(Company, through='TalentCompany')
    education = models.ManyToManyField(Education, through='TalentEducation')
    project = models.ManyToManyField(Projects, through='TalentProject')
    recruiter = models.ForeignKey(User, null=False, verbose_name='Recruiter ID')
    concepts = models.ManyToManyField(Concept, through='TalentConcept')
    current_location = models.CharField(max_length=255, verbose_name='Current Location', null=True, blank=True)
    rating = models.IntegerField(default=0)
    status = models.CharField(choices=TALENT_CHOICES, null=True, blank=True, max_length=40)
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


class TalentEmail(models.Model):
    talent = models.ForeignKey(Talent, related_name='talent_email')
    email = models.EmailField(max_length=100, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return self.talent.talent_name + self.email


class TalentContact(models.Model):
    talent = models.ForeignKey(Talent, related_name='talent_contact')
    contact = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=True)

    def __str__(self):
        return self.talent.talent_name + self.contact


class TalentEducation(models.Model):
    talent = models.ForeignKey(Talent, related_name='talent_education')
    education = models.ForeignKey(Education)
    course = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Talent Education History"

    def __str__(self):
        return self.talent.talent_name

    @property
    def get_start_date(self):
        return self.start_date.strftime('%d/%m/%Y')

    @property
    def get_end_date(self):
        return self.end_date.strftime('%d/%m/%Y')


class TalentCompany(models.Model):
    talent = models.ForeignKey(Talent, null=False, blank=True, verbose_name='Talent', related_name='talent_company')
    company = models.ForeignKey(Company, null=False, blank=True)
    designation = models.CharField(max_length=100, default='', null=True, blank=True)
    start_date = models.DateField(verbose_name='Start Date', null=True, blank=True)
    end_date = models.DateField(verbose_name='End Date', null=True, blank=True)
    is_current = models.BooleanField(verbose_name='Currently Working Here', default=False, null=False)

    class Meta:
        verbose_name_plural = "Talent Work History"
        db_table = 'talent_company_tb'
        ordering = ('-start_date', )
        
    @property
    def years_of_experience(self):
        return (self.end_date - self.start_date).days/365

    @property
    def get_start_date(self):
        return self.start_date.strftime('%d/%m/%Y')

    @property
    def get_end_date(self):
        return self.end_date.strftime('%d/%m/%Y')

    def __str__(self):
        return str(self.talent.talent_name + " works at " + self.company.company_name)


class TalentProject(models.Model):
    talent = models.ForeignKey(Talent, related_name='talent_project')
    project = models.ForeignKey(Projects)
    project_match = models.CharField(max_length=20, null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES)
    date_added = models.DateField(auto_now_add=True, null=True, blank=True)
    # last_update = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Talent Projects"
        ordering = ('-date_added',)

    @property
    def company_name(self):
        return self.project.company_name

    def get_date_added(self):
        return self.date_added.strftime('%d/%m/%Y')


class TalentConcept(models.Model):
    talent = models.ForeignKey(Talent, related_name='talent_concepts')
    concept = models.ForeignKey(Concept)
    match = models.CharField(max_length=10, default=0)
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Talent Concepts"

    def __str__(self):
        return self.concept.concept

    def get_date_created(self):
        return self.date_created.strftime('%d/%m/%Y')


class TalentStage(models.Model):
    talent = models.ForeignKey(Talent, related_name='talent_stages')
    project = models.ForeignKey(Projects)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    details = models.TextField(verbose_name='Details', null=True, blank=True)
    notes = models.TextField(verbose_name='Notes', null=True, blank=True)
    date_created = models.DateField(verbose_name='Create Date',auto_now_add=True)
    date_updated = models.DateField(verbose_name='Update Date',auto_now=True)

    def get_date_created(self):
        return self.date_created.strftime('%d/%m/%Y')

    def get_date_updated(self):
        return self.date_updated.strftime('%d/%m/%Y')


class ProjectConcept(models.Model):
    project = models.ForeignKey(Projects)
    concept = models.ForeignKey(Concept)
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Project TPConcept"

    def __str__(self):
        return self.concept.concept

    @property
    def project_name(self):
        return self.project.project_name


def get_upload_file_dir(instance, filename):
    return str(settings.PDF_UPLOAD_PATH + "/" + instance.user.username + "/" + filename)


def get_image_file_dir(instance):
    return str(settings.PDF_UPLOAD_PATH + "/" + instance.user.username + "/" + "images")


class FileUpload(models.Model):
    name = models.CharField(null=True, blank=True, max_length=200)
    file = models.FileField(upload_to=get_upload_file_dir)
    user = models.ForeignKey(User, null=True, blank=True)
    text = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return "{} uploaded {}".format(self.user.username, self.name)


class PdfImages(models.Model):
    name = models.CharField(null=True, blank=True, max_length=100)
    file = models.ForeignKey(FileUpload)
    image = models.ImageField(upload_to=get_image_file_dir, max_length=500)

    def __str__(self):
        return self.name
#
# @receiver(post_save, sender=FileUpload)
# def extract_image_from_file(sender, instance=None, created=False, **kwargs):
#     if created:
#         obj = sender()
#         obj.extract_text_from_pdf(instance)
#         obj.extract_image_from_pdf(instance, instance.file.path, "/images/")
