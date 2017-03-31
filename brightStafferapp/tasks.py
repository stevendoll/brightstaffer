from brightStaffer.celery import app
from django.core.management import call_command
import datetime
from brightStafferapp import models
from datetime import date
import textract
from ResumeParser.core import create_resume


@app.task
def add(x, y):
    return x + y


@app.task
def update_indexes():
    print("Indexing process started at {}".format(datetime.datetime.now()))
    call_command('update_index')
    print("Indexing process ended at {}".format(datetime.datetime.now()))


@app.task
def extract_text_from_pdf(file_upload_obj, user):
    """
    :param file_upload_obj: model object of the newly uploaded file. This object is already saved in database
    and is now sent to extract text from the pdf file
    :return: None or error
    """
    text = textract.process(file_upload_obj.file.path).decode('utf-8')
    file_upload_obj.text = text
    file_upload_obj.save()
    content = create_resume.create_resume(text)
    handle_talent_data(content, user)


def handle_talent_data(talent_data, user):
    if talent_data:
        if 'name' in talent_data and talent_data['name']:
            talent_obj = models.Talent.objects.create(talent_name=talent_data['name'], recruiter=user,
                                                      status='New', current_location='New Delhi',
                                                      linkedin_url='dndk', create_date=datetime.datetime.now())
            talent_recruiter, created = models.TalentRecruiter.objects.get_or_create(talent=talent_obj, recruiter=user,
                                                                              is_active=True)
            if talent_obj:
                if 'skills' in talent_data:
                    for skill in talent_data['skills']:
                        concept, created = models.Concept.objects.get_or_create(concept=skill['name'])
                        tpconcept, created = models.TalentConcept.objects.get_or_create(
                            talent=talent_obj, concept=concept,
                            match=str(round(skill['score'], 2)))
            if "work-experience" in talent_data:
                for experience in talent_data["work-experience"]:
                    is_current = False
                    # save all talent experience information
                    company, created = models.Company.objects.get_or_create(company_name=experience['Company'])
                    if experience['type'].lower() == "current":
                        is_current = True
                    start_date, end_date = convert_to_date(experience['Duration'])
                    if end_date == 'Present':
                        is_current = True
                        models.TalentCompany.objects.get_or_create(
                            talent=talent_obj, company=company, is_current=is_current,
                            designation=experience['JobTitle'], start_date=start_date)
                    else:
                        models.TalentCompany.objects.get_or_create(
                            talent=talent_obj, company=company, is_current=is_current,
                            designation=experience['JobTitle'], start_date=start_date, end_date=end_date)
            if "education" in talent_data:
                for education in talent_obj['education']:
                    # save user education information
                    org, created = models.Education.objects.get_or_create(name=education['organisation'])
                    start_date, end_date = convert_to_start_end(education['duration'])
                    if start_date and end_date:
                        tporg, created = models.TalentEducation.objects.get_or_create(talent=talent_obj, education=org,
                                                                                      course=education['course'],
                                                                                      start_date=start_date,
                                                                                      end_date=end_date
                                                                               )
                    else:
                        tporg, created = models.TalentEducation.objects.get_or_create(talent=talent_obj, education=org,
                                                                                      course=education['course'])
    else:
        pass


def convert_to_start_end(duration):
    start_date = None
    end_date = None
    day = 1
    month = 1
    if duration:
        duration = duration.split('-')
        start_year = duration[0]
        end_year = duration[1]
        start_date = date(int(start_year), month, day)
        end_date = date(int(end_year), month, day)
    return start_date, end_date


def convert_to_date(duration):
    month_arr = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }
    start_date = None
    end_date = None
    try:
        duration = duration.split('-')
        start_date = duration[0]
        start_date = start_date.split()
        month = start_date[0]
        year = start_date[1]
        day = 1
        start_date = date(int(year), int(month_arr[month]), int(day))
        end_date = duration[1]
        if end_date != 'Present':
            end_date = duration[1]
            end_date = end_date.split()
            month = end_date[0]
            year = end_date[1]
            day = 1
            end_date = date(int(year), int(month_arr[month]), int(day))
    except:
        pass
    return start_date, end_date
