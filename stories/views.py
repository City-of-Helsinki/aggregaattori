from django.contrib.gis.geos import Point
from munigeo.models import AdministrativeDivision
from rest_framework.decorators import api_view
from rest_framework.response import Response

from stories.models import Actor, Keyword, Story


def map_translated(story, translations, attribute):
    for language_code, value in translations.items():
        story.set_current_language(language_code)
        setattr(story, attribute, value)


@api_view(['POST'])
def import_activity_stream(request):
    story = Story()

    data = request.data

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

    # For now we just get the location based on the point and assign the
    # correct AdministrativeDivisions.
    location = obj['location']
    divisions = get_ocd_id(Point(location['longitude'], location['latitude']))

    story.save()
    # As locations and keywords are many-to-many relationships they need to be
    # set after saving.

    for division in divisions:
        story.locations.add(division)

    for tag in obj['tag']:
        keyword, _ = Keyword.objects.get_or_create(
            external_id=tag['id']
        )
        map_translated(keyword, tag['nameMap'], 'name')
        story.keywords.add(keyword)

    return Response(story.as_activity_stream())


def get_ocd_id(point):
    divisions = AdministrativeDivision.objects.filter(
        geometry__boundary__contains=point,
    )

    return divisions
