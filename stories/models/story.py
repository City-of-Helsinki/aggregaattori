from django.utils.translation import ugettext_lazy as _

from django.contrib.gis.db import models
from parler.models import TranslatableModel, TranslatedFields


class Story(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(
            verbose_name=_('Title'),
            max_length=100,
        ),
        text=models.TextField(
            verbose_name=_('Text'),
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
        null=True,
        blank=True,
    )
    location = models.GeometryField(
        verbose_name=_('Location'),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('Story')
        verbose_name_plural = _('Stories')

    def __unicode__(self):
        return self.title
