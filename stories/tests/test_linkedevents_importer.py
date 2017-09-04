# -*- coding: utf-8 -*-

import json

import pytest

from stories.importers import BaseAPIConsumer, LinkedeventsImporter
from stories.importers.linkedevents import strip_format_parameter
from stories.views import import_activity_stream


class TestAPIConsumer(BaseAPIConsumer):
    """
    This replaces the BaseAPIConsumer for tests.
    Basically it reads from files instead of over the network.
    """
    def fetch_items(self):
        return json.loads(open(self.target, 'r', encoding='utf8').read())


def get_importer(filename):
    importer = LinkedeventsImporter()
    importer.consumer = TestAPIConsumer()
    importer.consumer.target = filename
    return importer


@pytest.mark.django_db
def test_zero_linkedevent_importer():
    importer = get_importer('stories/tests/linkedevents.empty.json')
    events = []
    for event in importer:
        events.append(event)

    assert len(events) == 0


@pytest.mark.django_db
def test_single_linkedevent_importer():
    importer = get_importer('stories/tests/linkedevents.single.json')

    event = next(importer)

    assert event == get_expected_dict()


@pytest.mark.django_db
def test_multiple_linkedevent_importer():
    importer = get_importer('stories/tests/linkedevents.multiple.json')
    events = []
    for event in importer:
        events.append(event)

    assert len(events) == 4


@pytest.mark.django_db
def test_activity_type_update():
    importer = get_importer('stories/tests/linkedevents.single.json')
    event = next(importer)

    event['actor'] = {
        'id': 'actor-1234',
        'name': 'Test Actor',
        'type': 'Organization',
    }

    import_activity_stream(event)

    importer = get_importer('stories/tests/linkedevents.single.json')
    event = next(importer)

    expected_updated = get_expected_dict()
    expected_updated['type'] = 'Update'
    expected_updated['summaryMap'] = {
        'en': 'An unnamed organization updated the event Lörem ipsum dölör sit ämåt',
        'fi': 'Nimetön organisaatio päivitti tapahtuman Lörem ipsum dölör sit ämåt',
        'sv': 'En namnlös organisation updated the event Lörem ipsum dölör sit ämåt'
    }

    assert event == expected_updated


def get_expected_dict():
    return {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'actor': None,
        'generator': 'https://api.hel.fi/linkedevents/v1/event',
        'object': {
            'id': 'https://id.hel.fi/event/linkedevents:test-1234',
            'location': {
                'divisions': [{
                    'municipality': None,
                    'name': {
                        'fi': 'Helsinki',
                        'sv': 'Helsingfors'
                    },
                    'ocd_id': 'ocd-division/country:fi/kunta:helsinki',
                    'type': 'muni'
                }, {
                    'municipality': 'Helsinki',
                    'name': {
                        'fi': 'Mellunkylä',
                        'sv': 'Mellungsby'
                    },
                    'ocd_id': 'ocd-division/country:fi/kunta:helsinki/peruspiiri:mellunkylä',
                    'type': 'district'
                }, {
                    'municipality': 'Helsinki',
                    'name': {
                        'fi': 'Mellunkylä',
                        'sv': 'Mellungsby'
                    },
                    'ocd_id': 'ocd-division/country:fi/kunta:helsinki/kaupunginosa:mellunkylä',
                    'type': 'neighborhood'
                }, {
                    'municipality': 'Helsinki',
                    'name': {
                        'fi': 'Kontula',
                        'sv': 'Gårdsbacka'
                    },
                    'ocd_id': 'ocd-division/country:fi/kunta:helsinki/osa-alue:kontula',
                    'type': 'sub_district'
                }],
                'id': 'https://id.hel.fi/unit/tprek:1955',
                'latitude': 60.243496,
                'longitude': 25.08474,
                'nameMap': {
                    'en': 'Kontula comprehensive service '
                          'centre / Service centre',
                    'fi': 'Kontulan monipuolinen '
                          'palvelukeskus',
                    'sv': 'Gårdsbacka mångsidiga '
                          'servicecentral / Servicecentralen'
                },
                'type': 'Place'
            },
            'nameMap': {
                'fi': 'Lörem ipsum dölör sit ämåt'
            },
            'tag': [{
                'id': 'https://api.hel.fi/linkedevents/v1/keyword/yso:p18105/',
                'nameMap': {
                    'en': 'discussion groups',
                    'fi': 'keskusteluryhmät',
                    'sv': 'diskussionsgrupper'
                }
            }, {
                'id': 'https://api.hel.fi/linkedevents/v1/keyword/yso:p2434/',
                'nameMap': {
                    'en': 'elderly',
                    'fi': 'vanhukset',
                    'sv': 'åldringar'
                }
            }],
            'type': 'Event'
        },
        'published': None,
        'summaryMap': {
            'en': 'An unnamed organization announced the event Lörem ipsum '
                  'dölör sit ämåt',
            'fi': 'Nimetön organisaatio lisäsi tapahtuman Lörem ipsum '
                  'dölör sit ämåt',
            'sv': 'En namnlös organisation skapade evenemanget Lörem ipsum '
                  'dölör sit ämåt'
        },
        'type': 'Announce'
    }


@pytest.mark.parametrize('url,expected', [
    (None, None),
    ('', ''),
    ('test', 'test'),
    ('tprek:1955', 'tprek:1955'),
    ('https://api.hel.fi/linkedevents/v1/place/tprek:1955/', 'https://api.hel.fi/linkedevents/v1/place/tprek:1955/'),

    ('https://api.hel.fi/linkedevents/v1/place/tprek:1955/?format=json',
     'https://api.hel.fi/linkedevents/v1/place/tprek:1955/'),

    ('https://api.hel.fi/linkedevents/v1/keyword/yso:p11185/?format=json',
     'https://api.hel.fi/linkedevents/v1/keyword/yso:p11185/'),

    ('https://api.hel.fi/linkedevents/v1/keyword/yso:p11185/?format=json&testparam=1',
     'https://api.hel.fi/linkedevents/v1/keyword/yso:p11185/?testparam=1'),

    ('http://www.w3.org/2001/XMLSchema#dateTime', 'http://www.w3.org/2001/XMLSchema#dateTime'),
    ('http://www.w3.org/2001/XMLSchema?format=json#dateTime', 'http://www.w3.org/2001/XMLSchema#dateTime'),
])
def test_strip_format_url_parameter(url, expected):
    assert strip_format_parameter(url) == expected
