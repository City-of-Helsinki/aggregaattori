from jsonschema import validate, ValidationError as JsonSchemaValidationError
from rest_framework.exceptions import ValidationError as RestValidationError


class ActivityStreamsValidator:
    # TODO: Replace with a full Activity Streams 2 JSON Schema
    activity_streams_schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Activity Streams 2",
        "type": "object",
        "properties": {
            "@context": {
                "type": "string",
                "enum": ["https://www.w3.org/ns/activitystreams"],
            },
            "type": {
                "description": "The activity type",
                "type": "string",
                "enum": ["Update", "Announce"],
            },
            "object": {
                "type": "object",
                "properties": {
                    "id": {
                        "anyOf": [{
                            "type": "string"
                        }, {
                            "type": "number"
                        }]
                    }
                },
                "required": ["id"],
            },
        },
        "required": ["@context", "type"],
    }

    def __call__(self, attrs):
        try:
            validate(attrs, self.activity_streams_schema)
        except JsonSchemaValidationError as e:
            raise RestValidationError(e.message)
