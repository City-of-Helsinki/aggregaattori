import pytest

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
