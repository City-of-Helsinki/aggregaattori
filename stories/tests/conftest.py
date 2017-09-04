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
