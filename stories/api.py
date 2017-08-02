from rest_framework import generics, mixins, routers, serializers, viewsets
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from parler_rest.serializers import (
    TranslatableModelSerializer,
    TranslatedFieldsField,
)

from .models import Story, Keyword

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
            keyword, created = Keyword.objects.get_or_create(
                yso=yso_id,
            )
            pks.append(keyword.pk)
        return pks


class StorySerializer(TranslatableModelSerializer, GeoFeatureModelSerializer):
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

    class Meta:
        model = Story
        fields = (
            'id',
            'external_id',
            'keywords',
            'location',
            'location_id',
            'translations',
        )
        geo_field = 'location'


class StoryViewSet(
    generics.RetrieveUpdateDestroyAPIView,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    lookup_field = 'external_id'
    # This is needed to let get_object tell update about creation without
    # changing get_object.
    created = False

    def get_object(self, *args, **kwargs):
        if self.request.method == 'PUT':
            story, created = Story.objects.get_or_create(
                external_id=self.kwargs.get('external_id'),
            )
            self.created = created
            return story
        else:
            return super().get_object()

    def update(self, request, external_id=None, pk=None):
        response = super().update(request, external_id, pk)
        if self.created and response.status_code == 200:
            response.status_code = 201
        return response


register_view(StoryViewSet, 'story')
