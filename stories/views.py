from django.contrib.gis.geos import Point
from munigeo.models import AdministrativeDivision
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from stories.models import Actor, Keyword, Story


def map_translated(story, translations, attribute):
    for language_code, value in translations.items():
        story.set_current_language(language_code)
        setattr(story, attribute, value)


@api_view(['POST'])
def import_activity_streams(request):
    data = request.data
    responses = []

    if isinstance(request.data, list):
        for data in request.data:
            responses.append(import_activity_stream(data))
    elif isinstance(request.data, dict):
        responses.append(import_activity_stream(data))
    return Response(responses, status=status.HTTP_201_CREATED)


def import_activity_stream(data):
    # Simple check for a duplicate activity
    try:
        existing_story = Story.objects.get(json=data)
        return existing_story.as_activity_stream()
    except Story.DoesNotExist:
        pass

    # TODO: Data validation

    story = Story()

    story.published = data['published']
    map_translated(story, data['summaryMap'], 'summary')
    story.type = data['type']
    actor, _ = Actor.objects.get_or_create(
        external_id=data['actor']['id'],
        name=data['actor']['name'],
        type=data['actor']['type'],
    )
    story.actor = actor
    story.generator = data['generator']

    obj = data['object']
    story.external_id = obj['id']
    story.type = obj['type']
    map_translated(story, obj['nameMap'], 'name')

    story.json = data

    story.save()
    # As locations and keywords are many-to-many relationships they need to be
    # set after saving.

    # For now we just get the location based on the point and assign the
    # correct AdministrativeDivisions.
    for division in AdministrativeDivision.objects.filter(
            geometry__boundary__contains=Point(obj['location']['longitude'], obj['location']['latitude'])):
        story.locations.add(division)

    for tag in obj['tag']:
        keyword, _ = Keyword.objects.get_or_create(
            external_id=tag['id']
        )
        map_translated(keyword, tag['nameMap'], 'name')
        story.keywords.add(keyword)

    return story.as_activity_stream()


def get_ocd_id(point):
    divisions = AdministrativeDivision.objects.filter(
        geometry__boundary__contains=point,
    )

    return divisions
