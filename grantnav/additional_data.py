import jsonref
from django.conf import settings


def flatten_schema_titles(schema, path='', title_path=''):
    """Walk a JSON Schema, yielding (field_path, title_path) pairs for each leaf field.

    Mirrors the path-joining convention used by flatten_dict below, so the
    result can be used as a field-path -> title lookup when flattening data.
    """
    for field, property in schema.get('properties', {}).items():
        reference = getattr(property, '__reference__', {})
        title = property.get("title") or reference.get("title") or field
        next_path = (path + ': ' + field).lstrip(': ')
        next_title_path = (title_path + ': ' + title).lstrip(': ')

        if property['type'] == 'object':
            nested_schema = property
        elif property['type'] == 'array' and property['items']['type'] == 'object':
            nested_schema = property['items']
        else:
            nested_schema = None

        if nested_schema is not None:
            yield from flatten_schema_titles(nested_schema, next_path, next_title_path)
        else:
            yield next_path, next_title_path


def flatten_dict(data, path=tuple(), schema_titles=None):
    """Flatten a nested dict, yielding (field, title, value) triples.

    `field` is the stable schema field path (e.g. "grantPurpose") and should
    be used for any logic that depends on which field this is; `title` is
    the human-readable label to display and may change if the schema's
    title wording changes.
    """
    schema_titles = schema_titles or {}

    for key, value in data.items():
        field = ": ".join(path + (key,))
        title = schema_titles.get(field) or field

        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    yield from flatten_dict(item, path + (key,), schema_titles)
            strings = [item for item in value if isinstance(item, str) and item.strip()]
            if strings:
                yield field, title, ", ".join(strings)
        elif isinstance(value, dict):
            yield from flatten_dict(value, path + (key,), schema_titles)
        elif value is not None and (not isinstance(value, str) or value.strip()):
            yield field, title, value


# Fetch the schema once on module load
try:
    additional_data_schema = jsonref.load_uri(settings.ADDITIONAL_DATA_SCHEMA)
except Exception as e:
    if settings.DEBUG:
        print(f"Warning: could not fetch additional data schema, falling back to displaying raw keys: {e}")
        additional_data_schema = {}
    else:
        raise e
