from django.core.management.base import BaseCommand

from stories.importers import LinkedeventsImporter


class Command(BaseCommand):
    def handle(self, *args, **options):
        LinkedeventsImporter()
