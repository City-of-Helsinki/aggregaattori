import requests
import json
from django.core.management.base import BaseCommand

from stories.importers import LinkedeventsImporter


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'address',
            type=str,
            help=(
                'The address of the server where stories are POSTed.'
                ' Example: http://127.0.0.1:8000/v1/story/'
            ),
        )

    def handle(self, *args, **options):
        for event in LinkedeventsImporter():
            requests.post(
                options['address'],
                data=json.dumps(event),
                headers={'Content-Type': 'application/json'},

            )
