from parler.models import TranslatableModel, TranslatedFields
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Keyword(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(
            verbose_name=_('Name'),
            max_length=255,
            blank=True,
        ),
    )

    external_id = models.CharField(
        max_length=255,
        unique=True,
    )


    class Meta:
        verbose_name = _('Keyword')
        verbose_name_plural = _('Keywords')
