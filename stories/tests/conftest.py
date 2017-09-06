import pytest
from django.core.management import call_command

from stories.models import Actor, Keyword, Story


@pytest.fixture()
def actor_factory():
    def create_instance(**args):
        return Actor.objects.create(**args)

    return create_instance


@pytest.fixture()
def story_factory():
    def create_instance(**args):
        return Story.objects.create(**args)

    return create_instance


@pytest.fixture()
def keyword_factory():
    def create_instance(**args):
        return Keyword.objects.create(**args)

    return create_instance


@pytest.fixture(scope='session')
def administrative_divisions(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'stories/tests/fixtures/administrativedivision_data.json.gz')


@pytest.fixture()
def sample_story_dict():
    return {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'actor': {
            "type": "Organization",
            "name": "Testiorganisaatio",
            "url": "https://myhelsinki.fi",
            "id": "http://id.hel.fi/organization/test:2345",
        },
        'generator': 'https://api.hel.fi/linkedevents/v1/event',
        'object': {
            'id': 'https://id.hel.fi/event/linkedevents:test-1234',
            'location': {
                'type': 'Place',
                'latitude': 60.243496,
                'longitude': 25.08474,
                'id': 'https://id.hel.fi/unit/tprek:1955',
                'nameMap': {
                    'en': 'Kontula comprehensive service '
                          'centre / Service centre',
                    'fi': 'Kontulan monipuolinen '
                          'palvelukeskus',
                    'sv': 'Gårdsbacka mångsidiga '
                          'servicecentral / Servicecentralen'
                },
                'divisions': ["ocd-division/country:fi/kunta:helsinki/osa-alue:kalasatama",
                    "ocd-division/country:fi/kunta:helsinki/kaupunginosa:sörnäinen",
                    "ocd-division/country:fi/kunta:helsinki/peruspiiri:kallio",
                    "ocd-division/country:fi/kunta:helsinki"]
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
