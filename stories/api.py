from parler_rest.serializers import (TranslatableModelSerializer,
                                     TranslatedFieldsField)
from rest_framework import mixins, routers, serializers, viewsets
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Keyword, Story

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


class KeywordsField(serializers.RelatedField):
    def to_representation(self, value):
        '''Returns an array of YSOs in string format.'''
        ysos = []
        for keyword in value.all():
            ysos.append(keyword.yso)
        return ysos

    def to_internal_value(self, yso_ids):
        '''Returns a list of primary keys of the keywords.'''
        pks = []
        for yso_id in yso_ids:
            keyword, _ = Keyword.objects.get_or_create(
                yso=yso_id,
            )
            pks.append(keyword.pk)
        return pks


class StorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(
        shared_model=Story,
    )

    external_id = serializers.CharField(
        max_length=255,
        allow_blank=False,
        required=False,
    )

    keywords = KeywordsField(
        queryset=Keyword.objects.all(),
        required=False,
    )

    ocd_id = serializers.CharField(
        read_only=True,
        required=False,
    )

    class Meta:
        model = Story
        fields = (
            'id',
            'external_id',
            'keywords',
            'locations',
            'ocd_id',
            'translations',
        )


class StoryViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                   mixins.ListModelMixin, viewsets.GenericViewSet):

    queryset = Story.objects.all()
    serializer_class = StorySerializer


register_view(StoryViewSet, 'story')
