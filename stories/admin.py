from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from munigeo.models import AdministrativeDivisionGeometry
from parler.admin import TranslatableAdmin

from stories.models import Story


class StoryAdmin(OSMGeoAdmin, TranslatableAdmin):
    pass

class AdministrativeDivisionGeometryAdmin(OSMGeoAdmin):
    pass

admin.site.register(Story, StoryAdmin)
admin.site.register(AdministrativeDivisionGeometry, AdministrativeDivisionGeometryAdmin)
