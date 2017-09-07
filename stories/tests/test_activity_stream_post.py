import json

import pytest
from rest_framework.test import APIClient

from stories.models import Story


@pytest.mark.django_db
def test_activity_stream_post(sample_story_dict):
    client = APIClient()
    url = 'http://testserver/v1/story/'

    response = client.post(url, json.dumps(sample_story_dict), content_type='application/activity+json')

    assert response.status_code == 201
    assert Story.objects.count() == 1


@pytest.mark.django_db
def test_import_activity_stream_prevent_duplicate(sample_story_dict):
    client = APIClient()
    url = 'http://testserver/v1/story/'

    response = client.post(url, json.dumps(sample_story_dict), content_type='application/activity+json')

    assert response.status_code == 201
    assert Story.objects.count() == 1

    response = client.post(url, json.dumps(sample_story_dict), content_type='application/activity+json')

    assert response.status_code == 201
    assert Story.objects.count() == 1
