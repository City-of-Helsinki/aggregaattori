from django.core.management.base import BaseCommand

from stories.importers import LinkedeventsImporter


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'address',
            type=str,
            help=(
                'The address of the server where stories are PUT.'
                ' Example: http://127.0.0.1:8000/v1/story/'
            ),
        )
        parser.add_argument(
            '--progress',
            default=False,
            action='store_true',
            dest='progress',
            help='Show progress percentage',
        )


    def handle(self, *args, **options):
        LinkedeventsImporter(options['address'], progress=options['progress'])
