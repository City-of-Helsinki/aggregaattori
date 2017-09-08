import json

import pytest

from stories.importers import KerroKantasiAPIConsumer, KerroKantasiImporter


class KerroKantasiFileConsumer(KerroKantasiAPIConsumer):
    def fetch_items(self):
        return json.loads(open(self.target, 'r', encoding='utf8').read())


def get_importer(filename):
    importer = KerroKantasiImporter()
    importer.consumer = KerroKantasiFileConsumer()
    importer.consumer.target = filename

    return importer


@pytest.mark.django_db
def test_single_kerrokantasi_importer():
    importer = get_importer('stories/tests/fixtures/kerrokantasi.single.json')

    hearing = next(importer)

    assert hearing == get_expected_dict()


def get_expected_dict():
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "actor": {
            "name": "Kaupunkisuunnitteluvirasto",
            "type": "Organization",
            "id": "http://id.hel.fi/organization/Kaupunkisuunnitteluvirasto"
        },
        "generator": "https://api.hel.fi/kerrokantasi/v1/hearing",
        "object": {
            "id": "https://id.hel.fi/hearing/pjrjbnBdiOiVp0X5IwcO1MR2m8U0wIGm",
            "nameMap": {
                "fi": "Miten hulevedet hallintaan ja hyötykäyttöön? Kerro mielipiteesi"
            },
            "tag": [{
                "id": "kerrokantasi:20",
                "nameMap": {
                    "fi": "Kadut"
                }
            }, {
                "id": "kerrokantasi:21",
                "nameMap": {
                    "fi": "Puistot"
                }
            }, {
                "id": "kerrokantasi:114",
                "nameMap": {
                    "fi": "ympäristö"
                }
            }, {
                "id": "kerrokantasi:115",
                "nameMap": {
                    "fi": "hulevedet"
                }
            }],
            "type": "Hearing"
        },
        "published": "2017-06-16T11:53:30.837588Z",
        "summaryMap": {
            "en": "Kaupunkisuunnitteluvirasto announced the hearing Miten "
                  "hulevedet hallintaan ja hyötykäyttöön? Kerro mielipiteesi",
            "fi": "Kaupunkisuunnitteluvirasto lisäsi kuulemisen Miten "
                  "hulevedet hallintaan ja hyötykäyttöön? Kerro mielipiteesi",
            "sv": "Kaupunkisuunnitteluvirasto lade till hörandet Miten "
                  "hulevedet hallintaan ja hyötykäyttöön? Kerro mielipiteesi"
        },
        "type": "Announce"
    }
