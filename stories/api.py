import collections

from django_filters import rest_framework as filters
from rest_framework import mixins, routers, status, viewsets
from rest_framework.response import Response
from rest_framework_gis.filters import InBBoxFilter

from stories.serializers import StoryActivityStreamsSerializer, StorySerializer

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


class StoryFilterSet(filters.FilterSet, filters.BaseCSVFilter):
    keywords = filters.CharFilter(name='keywords__external_id')

    class Meta:
        model = Story
        fields = ['keywords']


class StoryViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    filter_backends = (
        filters.DjangoFilterBackend,
        InBBoxFilter,
    )
    filter_class = StoryFilterSet
    bbox_filter_field = 'geometry'
    bbox_filter_include_overlapping = True
    activity_streams_serializer_class = StoryActivityStreamsSerializer

    def create(self, request, *args, **kwargs):
        many = False

        if isinstance(request.data, collections.Sequence) and not isinstance(request.data, str):
            many = True

        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self):
        context = self.get_serializer_context()

        format_query_param = self.settings.URL_FORMAT_OVERRIDE

        if (context.get('format') == 'as2' or context['request'].query_params.get(format_query_param) == 'as2' or
                context['request'].content_type == 'application/activity+json'):
            return self.activity_streams_serializer_class

        return self.serializer_class


register_view(StoryViewSet, 'story')
