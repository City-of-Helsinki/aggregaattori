from django.utils.translation import ugettext_lazy as _

from django.contrib.gis.db import models
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
    keywords = models.ManyToManyField(
        Keyword,
        related_name='stories',
        blank=True,
    )

    class Meta:
        verbose_name = _('Story')
        verbose_name_plural = _('Stories')

    def __unicode__(self):
        return self.title
