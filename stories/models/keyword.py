from django.db import models
from django.utils.translation import ugettext_lazy as _


class Keyword(models.Model):
    yso = models.CharField(
        max_length=255,
        unique=True,
    )

    class Meta:
        verbose_name = _('Keyword')
        verbose_name_plural = _('Keywords')
