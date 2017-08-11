import json
import urllib.parse
from django.conf import settings

import requests


def safe_get(event, attribute, language_code):
    field = event.get(attribute)

    if field is None:
        return None
    return field.get(language_code)


def show_progress(total, remaining):
    print('\r%.2f%%' % (total/remaining*100), end='')


def get_translations(language_code, event):
    translations = {}
    title = safe_get(event, 'name', language_code)
    text = safe_get(event, 'description', language_code)
    short_text = safe_get(event, 'short_description', language_code)
    url = safe_get(event, 'info_url', language_code)

    if title is None and text is None and url is None:
        return None

    if title is not None:
        translations['title'] = title

    if text is not None:
        translations['text'] = text

    if short_text is not None:
        translations['short_text'] = short_text

    if url is not None:
        translations['url'] = url

    return translations


def get_keywords(keyword_urls):
    '''For now just get the id from the url directly.'''
    ids = []
    for keyword_url in keyword_urls:
        ids.append(url_to_id(keyword_url['@id']))
    return ids


def url_to_id(url):
    parts = urllib.parse.urlparse(url)
    path = parts[2].split('/')
    return path[-2]


class LinkedeventsImporter:

    count = 0
    processed = 0
    page_size = 100

    locations = {}

    target = (
        'https://api.hel.fi/linkedevents/v1/event/'
        '?format=json'
        '&page_size=%s'
    ) % (page_size)

    def __init__(self, address, progress=False):
        self.own_url = address

        while self.target:
            try:
                events = requests.get(url=self.target).json()
            except requests.exceptions.RequestException as ex:
                print(ex)
                break
            self.target = events['meta']['next']
            self.count = events['meta']['count']

            for event in events['data']:
                status = self.process_event(event)
                if status not in [200, 201]:
                    print("Status code not OK or CREATED: %s" % str(status))
                    self.target = None
                    break
                self.processed = self.processed + 1
                if progress:
                    show_progress(self.processed, self.count)

    def process_event(self, event):
        external_id = event['id']
        translations = {}
        location_id = None
        position = None
        keywords = None

        for language_code, _ in settings.LANGUAGES:
            current_translations = get_translations(language_code, event)
            if current_translations is not None:
                translations[language_code] = current_translations

        if event['location'] is not None:
            location_id, position = self.get_location(event['location']['@id'])

        if event['keywords'] is not None:
            keywords = get_keywords(event['keywords'])

        json_event = json.dumps({
            'location_id': location_id,
            'location': position,
            'keywords': keywords,
            'translations': translations,
        })

        response = requests.put(
            self.own_url + external_id + '/',
            data=json_event,
            headers={'Content-type': 'application/json'},
        )
        return response.status_code

    def get_location(self, place_url):
        if place_url in self.locations:
            return self.locations[place_url]

        place = requests.get(place_url, params={'format': 'json'}).json()
        position = place['position']
        location_id = place['id']

        self.locations[place_url] = (location_id, position)
        return location_id, position
