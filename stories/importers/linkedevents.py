# -*- coding: utf-8 -*-

import datetime
import logging

import requests
from django.conf import settings

from stories.importers.base import BaseAPIConsumer


def get_any_language(dictionary, preferred):
    if dictionary is None:
        return ''

    if dictionary.get(preferred):
        return dictionary.get(preferred)

    for language_code, _ in settings.LANGUAGES:
        if dictionary.get(language_code):
            return dictionary.get(language_code)
    return ''


def safe_get(event, attribute, language_code):
    field = event.get(attribute)

    if field is None:
        return None
    return field.get(language_code)


def get_tags(event):
    tags = []
    for keyword in event['keywords']:
        tags.append({
            'id': keyword['@id'],
            'nameMap': keyword['name'],
        })
    return tags


def get_last_modified():
    # Placeholder for getting the timestamp of the last import
    return datetime.date.today() - datetime.timedelta(days=1)


def get_location(event):
    if event['location'] is None:
        return None

    location = event['location']
    coordinates = None

    if location['position']:
        coordinates = location['position']['coordinates']

    return {
        'type': 'Place',
        'latitude': coordinates[0],
        'longitude': coordinates[1],
        'id': 'https://id.hel.fi/unit/' + location['id'],
        'nameMap': location['name'],
        'divisions': location['divisions'],
    }


class LinkedeventsAPIConsumer(BaseAPIConsumer):
    page_size = 100

    def __init__(self):
        self.target = (
            'https://api.hel.fi/linkedevents/v1/event/'
            '?format=json'
            '&last_modified_since=' + get_last_modified().isoformat() +
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

        org_name = ''
        organization = self.get_organization(event)
        if organization is not None:
            org_name = organization.get('name')

        unknown_org_names = {
            'fi': 'Nimetön organisaatio',
            'sv': 'En namnlös organisation',
            'en': 'An unnamed organization',
        }

        summaries = {}
        summary_texts = {
            'fi': 'lisäsi tapahtuman',
            'sv': 'skapade evenemanget',
            'en': 'announced the event',
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
            'type': 'Announce',
            'published': event['date_published'],
            'generator': 'https://api.hel.fi/linkedevents/v1/event',
            'actor': organization,
            'object': {
                'id': 'https://id.hel.fi/event/' + event['id'],
                'nameMap': event['name'],
                'type': 'Event',
                'tag': get_tags(event),
                'location': get_location(event),
            },
        }
        return activity
