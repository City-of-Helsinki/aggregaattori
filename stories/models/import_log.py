from django.db import models


class ImportLog(models.Model):
    importer = models.CharField(max_length=255, blank=True)
    import_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        get_latest_by = 'import_time'
