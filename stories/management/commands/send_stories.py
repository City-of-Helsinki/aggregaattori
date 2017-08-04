from django.core.management.base import BaseCommand

from stories.models import Story


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'address',
            type=str,
            help=(
                'Address of the messaging service.'
            ),
        )

    def handle(self, *args, **options):
        stories = Story.objects.filter(sent=False)
        for story in stories:
            if story.send(address=options['address']):
                print("OK %s" % story.external_id)
            else:
                print("FAIL %s" % story.external_id)
