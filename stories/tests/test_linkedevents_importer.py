# -*- coding: utf-8 -*-

import json

from stories.importers import BaseAPIConsumer, LinkedeventsImporter


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


def test_zero_linkedevent_importer():
    importer = get_importer('stories/tests/linkedevents.empty.json')
    events = []
    for event in importer:
        events.append(event)

    assert len(events) == 0


def test_single_linkedevent_importer():
    importer = get_importer('stories/tests/linkedevents.single.json')

    event = next(importer)

    assert event == get_expected_dict()


def test_multiple_linkedevent_importer():
    importer = get_importer('stories/tests/linkedevents.multiple.json')
    events = []
    for event in importer:
        events.append(event)

    assert len(events) == 4


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
                'latitude': 25.08474,
                'longitude': 60.243496,
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
