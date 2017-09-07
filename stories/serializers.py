from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import APIException

from .models import Story
from .validators import ActivityStreamsValidator


class StorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(
        shared_model=Story,
    )

    external_id = serializers.CharField(
        max_length=255,
        allow_blank=False,
        required=False,
    )

    class Meta:
        model = Story
        fields = (
            'id',
            'external_id',
            'keywords',
            'locations',
            'type',
            'generator',
            'published',
            'translations',
        )


class StoryActivityStreamsSerializer(serializers.BaseSerializer):
    default_validators = [ActivityStreamsValidator()]

    def update(self, instance, validated_data):
        raise APIException(code=400, detail='Updating in Activity Streams 2 format not allowed')

    def to_internal_value(self, data):
        return data

    def create(self, validated_data):
        # Simple check for a duplicate activity
        try:
            story = Story.objects.get(json=validated_data)
            return story
        except Story.DoesNotExist:
            pass

        story = Story.create_from_activity_stream(validated_data)

        return story

    def to_representation(self, instance):
        return instance.json
