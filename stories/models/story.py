from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
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

        # YSOs would be sent to the server, user UUIDs would be returned

        # Until the service comes online it is mocked here.
        import uuid
        fake_uuids = []
        for i in range(3):
            fake_uuids.append(str(uuid.uuid4()))
        return fake_uuids

    def create_message(instance, user_uuids):
        recipients = []
        for user_uuid in user_uuids:
            recipients.append({'uuid': user_uuid})

        def translate_field(name, code):
            return instance.safe_translation_getter(
                name,
                language_code=language_code,
            )

        def add_template(text):
            # Placeholder
            return "<p>%s</p>" % text

        contents = []
        for language_code, language_name in settings.LANGUAGES:
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
        # TODO serialize the message and send it to the messaging service and
        # set the sent boolean to true upon success.
