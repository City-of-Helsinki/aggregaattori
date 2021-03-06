from django.db import models
from django.utils.translation import ugettext_lazy as _


class Actor(models.Model):
    external_id = models.CharField(
        verbose_name=_('External ID'),
        max_length=255,
        blank=True,
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        blank=True,
    )

    type = models.CharField(
        verbose_name=_('Type'),
        max_length=255,
        blank=True,
    )

    class Meta:
        verbose_name = _('Actor')
        verbose_name_plural = _('Actors')
