import uuid

import pytest
from munigeo.models import AdministrativeDivision, AdministrativeDivisionType

from stories.models import Story


@pytest.mark.django_db
def test_create_from_activity_stream_locations(sample_story_dict, administrative_divisions):
    story = Story.create_from_activity_stream(sample_story_dict)

    assert story.json == sample_story_dict

    assert story.locations.filter().count() == 4
    assert story.locations.filter(type__type='district').count() == 2

    expected_ocd_ids = {
        'ocd-division/country:fi/kunta:helsinki/peruspiiri:mellunkylä',
        'ocd-division/country:fi/kunta:helsinki/peruspiiri:kallio',
    }

    ocd_ids = set(story.locations.filter(type__type='district').values_list('ocd_id', flat=True))

    assert ocd_ids == expected_ocd_ids


@pytest.mark.django_db
def test_get_interested_request_params(story_factory, keyword_factory):
    keyword1 = keyword_factory(name='Keyword1', external_id='kw:1')
    keyword2 = keyword_factory(name='Keyword1', external_id='kw:2')

    ad_type = AdministrativeDivisionType.objects.create(type='district', name='District')
    ad_type2 = AdministrativeDivisionType.objects.create(type='rescue_area', name='Rescue Area')

    ad1 = AdministrativeDivision.objects.create(
        type=ad_type,
        ocd_id='ocd-division/country:fi/kunta:helsinki/peruspiiri:ullanlinna'
    )
    ad2 = AdministrativeDivision.objects.create(
        type=ad_type,
        ocd_id='ocd-division/country:fi/kunta:helsinki/peruspiiri:reijola'
    )
    ad3 = AdministrativeDivision.objects.create(
        type=ad_type2,
        ocd_id='ocd-division/country:fi/kunta:helsinki/suojelupiiri:koillinen'
    )

    story = story_factory(name='Test', type='Create', summary='Test Summary', content='Test Content',
                          url='http://www.example.com/test/', )

    story.keywords = [keyword1, keyword2]
    story.locations = [ad1, ad2, ad3]

    expected = {
        'division': ['ocd-division/country:fi/kunta:helsinki/peruspiiri:ullanlinna',
                     'ocd-division/country:fi/kunta:helsinki/peruspiiri:reijola'],
        'yso': ['kw:1', 'kw:2'],
    }

    request_params = story.get_interested_request_params()

    assert sorted(request_params['division']) == sorted(expected['division'])
    assert sorted(request_params['yso']) == sorted(expected['yso'])


@pytest.mark.django_db
def test_create_message(settings, story_factory, keyword_factory):
    settings.EMAIL_FROM_NAME = 'From Name'
    settings.EMAIL_FROM_ADDRESS = 'from@example.com'
    settings.LANGUAGES = (('en', 'English'), ('fi', 'Finnish'),)

    story = story_factory(name='Test', type='Create', summary='Test Summary', content='Test Content',
                          url='http://www.example.com/test/')

    user_uuids = [str(uuid.uuid4()), str(uuid.uuid4())]

    expected = {
        'from_name': 'From Name',
        'from_email': 'from@example.com',
        'recipients': [{
            "uuid": val
        } for val in user_uuids],
        'contents': [{
            'html': '<p>Test Content</p>',
            'language': 'en',
            'short_text': 'Test Summary',
            'subject': 'Test Summary',
            'text': 'Test Content',
            'url': 'http://www.example.com/test/'
        }, {
            'html': '<p>Test Content</p>',
            'language': 'fi',
            'short_text': 'Test Summary',
            'subject': 'Test Summary',
            'text': 'Test Content',
            'url': 'http://www.example.com/test/'
        }],
    }

    message = story.create_message(user_uuids)

    assert message == expected
