from brightStaffer.celery import app
from django.core.management import call_command
import datetime


@app.task
def add(x, y):
    return x + y


@app.task
def update_indexes():
    print("Indexing process started at {}".format(datetime.datetime.now()))
    call_command('update_index')
    print("Indexing process ended at {}".format(datetime.datetime.now()))