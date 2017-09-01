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
        self.stdout.write('Sending unsent stories.')
        stories = Story.objects.filter(sent=False)

        self.stdout.write('{} unsent stories found.'.format(stories.count()))

        for story in stories:
            self.stdout.write('Story {}...'.format(story.external_id), ending='')

            if story.send(address=options['address']):
                self.stdout.write('Sent.')
            else:
                self.stdout.write('Fail or no interested users.')
