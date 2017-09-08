import datetime
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django.conf import settings
from django.utils import timezone

from stories.models import ImportLog


def get_any_language(dictionary, preferred):
    if dictionary is None:
        return ''

    if dictionary.get(preferred):
        return dictionary.get(preferred)

    for language_code, _ in settings.LANGUAGES:
        if dictionary.get(language_code):
            return dictionary.get(language_code)
    return ''


def safe_get(event, attribute, language_code):
    field = event.get(attribute)

    if field is None:
        return None
    return field.get(language_code)


def strip_format_parameter(url):
    if url is None:
        return url

    try:
        parsed = urlparse(url)

        query = parse_qs(parsed.query)
        query.pop('format', None)
        new_query = urlencode(query, True)

        new_parts = list(parsed)
        new_parts[4] = new_query

        new_url = urlunparse(new_parts)

        return new_url
    except ValueError:
        return url


def get_last_modified(importer_name=None, days=1):
    latest = None
    try:
        latest = ImportLog.objects.filter(importer=importer_name).latest()
    except ImportLog.DoesNotExist:
        pass

    if not latest:
        return timezone.now() - datetime.timedelta(days=days)

    return latest.import_time
