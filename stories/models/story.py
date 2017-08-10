import json

import requests
from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from munigeo.models import AdministrativeDivision
from parler.models import TranslatableModel, TranslatedFields

from .keyword import Keyword


class Story(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(
            verbose_name=_('Title'),
            max_length=255,
        ),
        text=models.TextField(
            verbose_name=_('Text'),
            blank=True,
        ),
        short_text=models.TextField(
            verbose_name=_('Short text'),
            blank=True,
        ),
        url=models.URLField(
            verbose_name=_('URL'),
            blank=True,
        )
    )

    external_id = models.CharField(
        max_length=255,
        unique=True,
    )
    location = models.GeometryField(
        verbose_name=_('Location'),
        null=True,
        blank=True,
    )
    location_id = models.CharField(
        max_length=255,
        blank=True,
    )
    ocd_id = models.CharField(
        max_length=255,
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

    class Meta:
        verbose_name = _('Story')
        verbose_name_plural = _('Stories')

    def __unicode__(self):
        return self.title

    def get_interested_users(self):
        # This project uses YSO for identifying keywords.
        # For more information see https://finto.fi/yso/en/
        ysos = []
        for keyword in self.keywords.all():
            ysos.append(keyword.yso)

        url = '%s/interested/' % (settings.TUNNISTAMO_URL)

        params = {
            'division': self.ocd_id,
            'yso': ','.join(ysos),
        }

        return requests.get(url, params=params).json()

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
        for language_code, _ in settings.LANGUAGES:
            contents.append({
                'language': language_code,
                'subject': translate_field('title', language_code),
                'url': translate_field('url', language_code),
                'text': translate_field('text', language_code),
                'html': add_template(translate_field('text', language_code)),
                'short_text': translate_field('short_text', language_code),
            })

        return {
            'from_name': settings.EMAIL_FROM_NAME,
            'from_email': settings.EMAIL_FROM_ADDRESS,
            'recipients': recipients,
            'contents': contents,
        }

    def send(self, address):
        message = self.create_message(self.get_interested_users())

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

    def set_ocd_id(self):
        if self.location is None:
            return

        divisions = AdministrativeDivision.objects.filter(
            geometry__boundary__contains=self.location,
        )

        for division in divisions:
            if division.type.type == 'district':
                self.ocd_id = division.ocd_id

    def save(self, *args, **kwargs):
        self.set_ocd_id()
        super().save(*args, **kwargs)
