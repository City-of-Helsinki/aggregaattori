from rest_framework import routers, serializers, viewsets
from parler_rest.serializers import (
    TranslatableModelSerializer,
    TranslatedFieldsField,
)

from .models import Story

all_views = []


def register_view(klass, name, base_name=None):
    entry = {'class': klass, 'name': name}
    if base_name is not None:
        entry['base_name'] = base_name
    all_views.append(entry)


class APIRouter(routers.DefaultRouter):
    def __init__(self):
        super().__init__()
        self.registered_api_views = set()
        self._register_all_views()

    def _register_view(self, view):
        if view['class'] in self.registered_api_views:
            return
        self.registered_api_views.add(view['class'])
        self.register(view['name'], view['class'], base_name=view.get("base_name"))

    def _register_all_views(self):
        for view in all_views:
            self._register_view(view)


class StorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Story)

    class Meta:
        model = Story
        fields = ('id', 'url', 'location', 'translations')


class StoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer


register_view(StoryViewSet, 'story')
