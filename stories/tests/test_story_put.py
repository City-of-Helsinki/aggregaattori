import pytest
from rest_framework.test import APIClient


class TestStoryPut:
    client = APIClient()
    url = 'http://testserver/v1/story/test:1234/'

    story = {
        "location": {
            "type": "Point",
            "coordinates": [
                25.000000,
                60.170833
            ]
        },
        "keywords": [
            "yso:p8471"
        ],
        "ocd_id": "test",
        "translations": {
            "en": {
                "title":"English test title",
                "short_text": "Short text.",
                "text": "English test text.",
                "url": "http://example.org/en"
            }
        }
    }

    @pytest.mark.django_db
    def test__put_create(self):

        response = self.client.put(
            self.url,
            self.story,
            format='json',
        )

        assert response.status_code == 201

    @pytest.mark.django_db
    def test__put_modify(self):
        response = self.client.put(
            self.url,
            self.story,
            format='json',
        )

        modified_story = self.story.copy()

        response = self.client.put(
            self.url,
            modified_story,
            format='json',
        )

        assert response.status_code == 200

    @pytest.mark.django_db
    def test__put_and_get_story(self):
        response = self.client.put(
            self.url,
            self.story,
            format='json',
        )

        response = self.client.get(self.url)
        response_story = response.json()

        assert response_story['properties']['external_id'] == 'test:1234'
        assert response_story['properties']['keywords'] == ["yso:p8471"]

        assert response.status_code == 200
