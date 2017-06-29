from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from parler.admin import TranslatableAdmin
from stories.models import Story


class StoryAdmin(OSMGeoAdmin, TranslatableAdmin):
    pass


admin.site.register(Story, StoryAdmin)
