import json

import dateutil.parser
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone

from stories.importers import KerroKantasiImporter, LinkedeventsImporter
from stories.importers.utils import get_last_modified
from stories.models import ImportLog


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'address',
            type=str,
            help=(
                'The address of the server where the imported stories are POSTed as an activity stream.'
                ' Example: http://127.0.0.1:8000/v1/story/'
            ),
        )

    def handle(self, *args, **options):
        for event in LinkedeventsImporter():
            requests.post(
                options['address'],
                data=json.dumps(event),
                headers={'Content-Type': 'application/activity+json'},
            )

        ImportLog.objects.create(importer='LinkedEventsImporter', import_time=timezone.now())

        latest_kerrokantasi_import = get_last_modified(importer_name='KerroKantasiImporter', days=180)

        for hearing in KerroKantasiImporter():
            try:
                published_datetime = dateutil.parser.parse(hearing.get('published'))

                if published_datetime > latest_kerrokantasi_import:
                    requests.post(
                        options['address'],
                        data=json.dumps(hearing),
                        headers={'Content-Type': 'application/activity+json'}
                    )
            except (ValueError, TypeError):
                pass

        ImportLog.objects.create(importer='KerroKantasiImporter', import_time=timezone.now())
