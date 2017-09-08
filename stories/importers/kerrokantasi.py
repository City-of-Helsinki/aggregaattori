import logging
from urllib.parse import quote_plus

from django.conf import settings
from munigeo.models import AdministrativeDivision

from stories.importers.base import BaseAPIConsumer
from stories.importers.utils import get_any_language
from stories.models import Story


def get_tags(hearing):
    tags = []
    for keyword in hearing['labels']:
        tags.append({
            'id': 'kerrokantasi:{}'.format(keyword['id']),
            'nameMap': keyword['label'],
        })

    return tags


def get_divisions(hearing):
    divisions = []
    for keyword in hearing['labels']:
        # Try to match label to a district for the location
        if keyword['label'].get('fi'):
            label_lowercase = keyword['label'].get('fi').lower()

            administrative_divisions = AdministrativeDivision.objects.filter(
                ocd_id__in=[
                    'ocd-division/country:fi/kunta:helsinki/suurpiiri:{}'.format(label_lowercase),
                    'ocd-division/country:fi/kunta:helsinki/peruspiiri:{}'.format(label_lowercase),
                    'ocd-division/country:fi/kunta:helsinki/osa-alue:{}'.format(label_lowercase),
                    'ocd-division/country:fi/kunta:helsinki/kaupunginosa:{}'.format(label_lowercase),
                    'ocd-division/country:fi/kunta:{}'.format(label_lowercase),
                ])

            for administrative_division in administrative_divisions:
                division = {
                    'type': administrative_division.type.type,
                    'ocd_id': administrative_division.ocd_id,
                    'municipality': None,
                    'name': administrative_division.name,
                }

                if administrative_division.municipality:
                    division['municipality'] = administrative_division.municipality.name

                divisions.append(division)

    return divisions


class KerroKantasiAPIConsumer(BaseAPIConsumer):
    page_size = 100

    def get_items_from_json(self, json_content):
        return json_content.get('results')

    def get_next_target_from_json(self, json_content):
        return json_content.get('next')

    def __init__(self):
        self.target = (
            'https://api.hel.fi/kerrokantasi/v1/hearing/'
            '?format=json'
            '&ordering=-created_at'
            '&limit={}'
        ).format(self.page_size)


class KerroKantasiImporter:
    consumer = None
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.consumer = KerroKantasiAPIConsumer()

    def __iter__(self):
        return self

    def __next__(self):
        return self.hearing_to_activity_stream(self.consumer.__next__())

    def hearing_to_activity_stream(self, hearing):
        hearing_id = 'https://id.hel.fi/hearing/{}'.format(hearing['id'])
        activity_type = 'Announce'
        organization = None
        summaries = {}
        contents = {}
        divisions = []

        org_name = hearing.get('organization')
        if org_name:
            organization = {
                'type': 'Organization',
                'name': org_name,
                # TODO: Need to find the real identifier somehow
                'id': 'http://id.hel.fi/organization/{}'.format(quote_plus(org_name)),
            }

        unknown_org_names = {
            'fi': 'Nimetön organisaatio',
            'sv': 'En namnlös organisation',
            'en': 'An unnamed organization',
        }

        # TODO: The activity type is set to Update if there is a Story with the same id already in the system.
        # This is just for proof of concept purposes.
        if Story.objects.filter(external_id=hearing_id).exists():
            activity_type = 'Update'

        verb_texts = {
            'fi': 'lisäsi kuulemisen',
            'sv': 'lade till hörandet',
            'en': 'announced the hearing',
        }

        if activity_type == 'Update':
            verb_texts = {
                'fi': 'päivitti kuulemisen',
                'sv': 'uppdaterade hörandet',
                'en': 'updated the hearing',
            }

        for language_code, _ in settings.LANGUAGES:
            if not org_name:
                used_org_name = unknown_org_names[language_code]
            else:
                used_org_name = org_name

            summaries[language_code] = "{organization_name} {verb} {title}".format(
                organization_name=used_org_name,
                verb=verb_texts[language_code],
                title=get_any_language(hearing['title'], language_code),
            )

            abstract = get_any_language(hearing['abstract'], language_code)
            if abstract:
                contents[language_code] = abstract

        tags = get_tags(hearing)
        divisions = get_divisions(hearing)

        activity = {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'summaryMap': summaries,
            'type': activity_type,
            'published': hearing['created_at'],
            'generator': 'https://api.hel.fi/kerrokantasi/v1/hearing',
            'actor': organization,
            'object': {
                'id': hearing_id,
                'nameMap': hearing['title'],
                'type': 'Hearing',
                'tag': tags,
            },
        }

        if contents:
            activity['contentMap'] = contents

        if divisions:
            activity['object']['location'] = {
                'divisions': divisions,
            }

        return activity
