import pytest
from rest_framework.test import APIClient


class TestStory:
    client = APIClient()
    url = 'http://testserver/v1/story/'

    story = {
        "external_id": "test:1234",
        "location": {
            "type": "Point",
            "coordinates": [
                25.000000,
                60.170833
            ]
        },
        "keywords": [
            "yso:p8471",
            "yso:p26360"
        ],
        "ocd_id": "This should be overridden",
        "translations": {
            "en": {
                "title": "English test title",
                "short_text": "Short text.",
                "text": "English test text.",
                "url": "http://example.org/en"
            }
        }
    }

    @pytest.mark.django_db
    def test__post(self):

        response = self.client.post(
            self.url,
            self.story,
            format='json',
        )

        assert response.status_code == 201

    @pytest.mark.django_db
    def test__put(self):

        response = self.client.post(
            self.url,
            self.story,
            format='json',
        )

        story = response.json()

        assert response.status_code == 201

        modified_story = self.story.copy()

        response = self.client.put(
            self.url + str(story['id']) + '/',
            modified_story,
            format='json',
        )

        assert response.status_code == 200

    @pytest.mark.django_db
    def test__put_changes_content(self):
        response = self.client.post(
            self.url,
            self.story,
            format='json',
        )
        story = response.json()

        response = self.client.get(self.url + str(story['id']) + '/')
        response_story = response.json()

        assert response_story['external_id'] == 'test:1234'
        assert response_story['keywords'] == [
            "yso:p8471",
            "yso:p26360",
        ]

        assert response.status_code == 200
