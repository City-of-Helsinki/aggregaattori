import json

import requests
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from munigeo.models import AdministrativeDivision
from parler.models import TranslatableModel, TranslatedFields
from requests import RequestException

from .actor import Actor
from .keyword import Keyword


class Story(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(
            verbose_name=_('Name'),
            max_length=255,
            blank=True,
        ),

        content=models.TextField(
            verbose_name=_('Content'),
            blank=True,
        ),

        summary=models.TextField(
            verbose_name=_('Summary'),
            blank=True,
        ),

        url=models.URLField(
            verbose_name=_('URL'),
            blank=True,
        )
    )

    external_id = models.CharField(
        max_length=255,
        unique=False,
    )

    type = models.CharField(
        max_length=32,
    )

    published = models.DateTimeField(
        blank=True,
        null=True,
    )

    generator = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    actor = models.ForeignKey(
        Actor,
        blank=True,
        null=True,
    )

    locations = models.ManyToManyField(
        AdministrativeDivision,
        related_name='stories',
        blank=True,
    )

    keywords = models.ManyToManyField(
        Keyword,
        related_name='stories',
        blank=True,
    )

    sent = models.BooleanField(
        default=False,
    )

    json = JSONField(
        blank=True,
        null=True,
    )

    geometry = models.GeometryField(
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _('Story')
        verbose_name_plural = _('Stories')

    def __unicode__(self):
        return self.title

    @staticmethod
    def create_from_activity_stream(data):
        def map_translated(instance, translations, attribute):
            for language_code, value in translations.items():
                instance.set_current_language(language_code)
                setattr(instance, attribute, value)

        story = Story()
        story.json = data
        story.generator = data['generator']
        story.published = data['published']
        map_translated(story, data['summaryMap'], 'summary')
        story.type = data['type']

        if data.get('actor'):
            (actor, created) = Actor.objects.get_or_create(external_id=data['actor']['id'], name=data['actor']['name'],
                                                           type=data['actor']['type'])
            story.actor = actor

        obj = data['object']
        story.external_id = obj['id']
        story.type = obj['type']
        map_translated(story, obj['nameMap'], 'name')

        locations = set()

        location = obj.get('location') or {}

        longitude = location.get('longitude')
        latitude = location.get('latitude')

        if longitude and latitude:
            point = Point(longitude, latitude)
            story.geometry = point
            for administrative_division in AdministrativeDivision.objects.filter(
                    geometry__boundary__contains=point):
                locations.add(administrative_division)

        story.save()

        if location.get('divisions'):
            for administrative_division in AdministrativeDivision.objects.filter(
                    ocd_id__in=location.get('divisions')):
                locations.add(administrative_division)

        story.locations = locations

        for tag in obj['tag']:
            (keyword, created) = Keyword.objects.get_or_create(external_id=tag['id'])
            map_translated(keyword, tag['nameMap'], 'name')
            story.keywords.add(keyword)

        return story

    def get_interested_request_params(self):
        # This project uses YSO for identifying keywords.
        # For more information see https://finto.fi/yso/en/
        params = {
            'division': [l.ocd_id for l in self.locations.filter(type__type='district')],
            'yso': [k.external_id for k in self.keywords.all()],
        }

        return params

    def get_interested_users(self):
        url = '%s/interested/' % (settings.TUNNISTAMO_URL)
        params = self.get_interested_request_params()

        try:
            r = requests.post(url, data=params, auth=(settings.TUNNISTAMO_USERNAME, settings.TUNNISTAMO_PASSWORD))

            r.raise_for_status()

            return r.json()
        except RequestException as e:
            # TODO: Log error and try again later
            return []

    def create_message(self, user_uuids):
        recipients = []
        for user_uuid in user_uuids:
            recipients.append({'uuid': user_uuid})

        def translate_field(name, code):
            return self.safe_translation_getter(
                name,
                language_code=code,
            )

        def add_template(text):
            # Placeholder
            return "<p>%s</p>" % text

        contents = []
        for language_code, language_name in settings.LANGUAGES:
            contents.append({
                'language': language_code,
                'subject': translate_field('summary', language_code),
                'url': translate_field('url', language_code),
                'text': translate_field('content', language_code),
                'html': add_template(translate_field('content', language_code)),
                'short_text': translate_field('summary', language_code),
            })

        return {
            'from_name': settings.EMAIL_FROM_NAME,
            'from_email': settings.EMAIL_FROM_ADDRESS,
            'recipients': recipients,
            'contents': contents,
        }

    def send(self, address):
        user_uuids = self.get_interested_users()

        if not user_uuids:
            # No interested users, save as sent for now.
            self.sent = True
            self.save()

            return False

        message = self.create_message(user_uuids)

        response = requests.post(
            address,
            data=json.dumps(message),
            headers={'Content-type': 'application/json'},
            auth=(settings.EMAIL_AUTH_NAME, settings.EMAIL_AUTH_PASS),
        )

        if response.status_code != 201:
            return False

        self.sent = True
        self.save()

        return True
