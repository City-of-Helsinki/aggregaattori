import pytest
from rest_framework.test import APIClient


class TestStory:
    client = APIClient()
    url = 'http://testserver/v1/activity_stream/'

    story = {
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
                'latitude': 25.08474,
                'longitude': 60.243496,
                'id': 'https://id.hel.fi/unit/tprek:1955',
                'nameMap': {
                    'en': 'Kontula comprehensive service '
                          'centre / Service centre',
                    'fi': 'Kontulan monipuolinen '
                          'palvelukeskus',
                    'sv': 'Gårdsbacka mångsidiga '
                          'servicecentral / Servicecentralen'
                },
                'divisions': [
                    "ocd-division/country:fi/kunta:helsinki/osa-alue:kalasatama",
                    "ocd-division/country:fi/kunta:helsinki/kaupunginosa:sörnäinen",
                    "ocd-division/country:fi/kunta:helsinki/peruspiiri:kallio",
                    "ocd-division/country:fi/kunta:helsinki"
                ]
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

    @pytest.mark.django_db
    def test_post(self):

        response = self.client.post(
            self.url,
            self.story,
            format='json',
        )

        assert response.status_code == 201
