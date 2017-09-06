from rest_framework import renderers


class ActivityStreamsRenderer(renderers.JSONRenderer):
    media_type = 'application/activity+json'
    format = 'as2'
