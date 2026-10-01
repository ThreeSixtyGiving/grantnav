import jsonref
from django.conf import settings


def flatten_schema_titles(schema, path='', title_path=''):
    for field, property in schema.get('properties', {}).items():
        title = property.get('title') or getattr(property, '__reference__', {}).get('title') or field
        if property['type'] == 'array':
            if property['items']['type'] == 'object':
                yield from flatten_schema_titles(property['items'], path + ': ' + field, title_path + ': ' + title)
            else:
                yield ((path + ': ' + field).lstrip(': '), (title_path + ': ' + title).lstrip(': '))
        if property['type'] == 'object':
            yield from flatten_schema_titles(property, path + ': ' + field, title_path + ': ' + title)
        else:
            yield ((path + ': ' + field).lstrip(': '), (title_path + ': ' + title).lstrip(': '))


def flatten_dict(data, path=tuple(), schema_titles=None):
    schema_titles = schema_titles or {}

    for key, value in data.items():
        field = ": ".join(path + (key,))
        if isinstance(value, list):
            string_list = []
            for item in value:
                if isinstance(item, dict):
                    yield from flatten_dict(item, path + (key,), schema_titles)
                if isinstance(item, str):
                    string_list.append(item)
            if string_list:
                yield schema_titles.get(field) or field, ", ".join(string_list)
        elif isinstance(value, dict):
            yield from flatten_dict(value, path + (key,), schema_titles)
        else:
            yield schema_titles.get(field) or field, value


# Fetch the schema once on module load
try:
    additional_data_schema = jsonref.load_uri(settings.ADDITIONAL_DATA_SCHEMA)
except Exception as e:
    if settings.DEBUG:
        print(f"Warning: could not fetch additional data schema, falling back to displaying raw keys: {e}")
        additional_data_schema = {}
    else:
        raise e
