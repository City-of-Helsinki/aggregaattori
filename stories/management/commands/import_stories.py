import json

import requests
from django.core.management.base import BaseCommand
from django.utils import timezone

from stories.importers import LinkedeventsImporter
from stories.models import ImportLog


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'address',
            type=str,
            help=(
                'The address of the server where the imported stories are POSTed as an activity stream.'
                ' Example: http://127.0.0.1:8000/v1/activity_stream/'
            ),
        )

    def handle(self, *args, **options):
        for event in LinkedeventsImporter():
            requests.post(
                options['address'],
                data=json.dumps(event),
                headers={'Content-Type': 'application/json'},
            )

        ImportLog.objects.create(importer='LinkedEventsImporter', import_time=timezone.now())
