from django.core.management.base import BaseCommand, CommandError
from brightStafferapp.search import rebuild_search

import datetime


class Command(BaseCommand):
    # help = "This command is for cleanup .. mainly in transaction session table"

    def handle(self, **options):
        print("Search index rebuild process started at %s\n" % str(datetime.datetime.now()))
        rebuild_search()
        print("Search index rebuild process ended at %s\n" % str(datetime.datetime.now()))
