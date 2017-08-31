from parler_rest.serializers import (TranslatableModelSerializer,
                                     TranslatedFieldsField)
from rest_framework import mixins, routers, serializers, viewsets

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
    translations = TranslatedFieldsField(
        shared_model=Story,
    )

    external_id = serializers.CharField(
        max_length=255,
        allow_blank=False,
        required=False,
    )

    class Meta:
        model = Story
        fields = (
            'id',
            'external_id',
            'keywords',
            'locations',
            'type',
            'generator',
            'published',
            'translations',
        )


class StoryViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                   mixins.ListModelMixin, viewsets.GenericViewSet):

    queryset = Story.objects.all()
    serializer_class = StorySerializer


register_view(StoryViewSet, 'story')
