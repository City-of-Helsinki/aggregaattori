from rest_framework.parsers import JSONParser

from . import renderers


class ActivityStreamsParser(JSONParser):
    media_type = 'application/activity+json'
    renderer_class = renderers.ActivityStreamsRenderer
