import logging

import requests
from django.conf import settings

from stories.importers.base import BaseAPIConsumer
from stories.importers.utils import (get_any_language, get_last_modified,
                                     strip_format_parameter)
from stories.models import Story


def get_tags(event):
    tags = []
    for keyword in event['keywords']:
        tags.append({
            'id': strip_format_parameter(keyword['@id']),
            'nameMap': keyword['name'],
        })
    return tags


def get_location(event):
    if event['location'] is None:
        return None

    location = event['location']
    coordinates = None

    if location['position']:
        coordinates = location['position']['coordinates']

    return {
        'type': 'Place',
        'latitude': coordinates[1],
        'longitude': coordinates[0],
        'id': 'https://id.hel.fi/unit/' + location['id'],
        'nameMap': location['name'],
        'divisions': location['divisions'],
    }


class LinkedeventsAPIConsumer(BaseAPIConsumer):
    page_size = 100

    def get_items_from_json(self, json_content):
        return json_content.get('data')

    def get_next_target_from_json(self, json_content):
        return json_content.get('meta', {}).get('next')

    def __init__(self):
        last_modified_string = get_last_modified(importer_name='LinkedEventsImporter', days=1).strftime(
            '%Y-%m-%dT%H:%M:%SZ')

        self.target = (
            'https://api.hel.fi/linkedevents/v1/event/'
            '?format=json'
            '&last_modified_since=' + last_modified_string +
            '&include=keywords,location'
            '&page_size=%s'
        ) % (self.page_size)


class LinkedeventsImporter:

    consumer = None

    logger = logging.getLogger(__name__)

    locations = {}
    organizations = {}
    keywords = {}

    def __init__(self):
        self.consumer = LinkedeventsAPIConsumer()

    def __iter__(self):
        return self

    def __next__(self):
        return self.event_to_activity_stream(self.consumer.__next__())

    def get_organization(self, event):
        if event['publisher'] is None:
            return None
        org_url = 'http://api.hel.fi/linkedevents/v1/organization/' + event['publisher']

        if org_url in self.organizations:
            return self.organizations[org_url]

        org = requests.get(org_url, params={'format': 'json'}).json()
        organization = {
            'type': 'Organization',
            'name': org['name'],
            'id': 'http://id.hel.fi/organization/' + org['id'],
        }

        self.organizations[org_url] = organization
        return organization

    def event_to_activity_stream(self, event):
        # Turns a single event into a simplified activity stream object,
        # because we don't care about all fields.

        event_id = 'https://id.hel.fi/event/{}'.format(event['id'])

        org_name = ''
        organization = self.get_organization(event)
        if organization is not None:
            org_name = organization.get('name')

        unknown_org_names = {
            'fi': 'Nimetön organisaatio',
            'sv': 'En namnlös organisation',
            'en': 'An unnamed organization',
        }

        activity_type = 'Announce'
        summaries = {}

        # TODO: The activity type is set to Update if there is a Story with the same id already in the system.
        # This is just for proof of concept purposes.
        if Story.objects.filter(external_id=event_id).exists():
            activity_type = 'Update'

        if activity_type == 'Announce':
            summary_texts = {
                'fi': 'lisäsi tapahtuman',
                'sv': 'skapade evenemanget',
                'en': 'announced the event',
            }
        elif activity_type == 'Update':
            summary_texts = {
                'fi': 'päivitti tapahtuman',
                'sv': 'uppdaterade evenemanget',
                'en': 'updated the event',
            }

        for language_code, _ in settings.LANGUAGES:
            used_org_name = ''
            if not org_name:
                used_org_name = unknown_org_names[language_code]
            else:
                used_org_name = org_name

            summaries[language_code] = "%s %s %s" % (
                used_org_name,
                summary_texts[language_code],
                get_any_language(event['name'], language_code),
            )

        activity = {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'summaryMap': summaries,
            'type': activity_type,
            'published': event['date_published'],
            'generator': 'https://api.hel.fi/linkedevents/v1/event',
            'actor': organization,
            'object': {
                'id': event_id,
                'nameMap': event['name'],
                'type': 'Event',
                'tag': get_tags(event),
                'location': get_location(event),
            },
        }
        return activity
