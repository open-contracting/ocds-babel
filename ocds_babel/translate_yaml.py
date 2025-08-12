from copy import deepcopy

import yaml

from ocds_babel.util import text_to_translate


# This should roughly match the logic of `extract_yaml`.
def translate_yaml(io, translator, keys=(), **kwargs):
    """Accept a YAML file as an IO object, and return its translated contents in YAML format."""
    data = yaml.safe_load(io)

    data = translate_yaml_data(data, translator, keys, **kwargs)

    return yaml.safe_dump(data, default_flow_style=False, allow_unicode=True)


def translate_yaml_data(source, translator, keys=(), **kwargs):
    """Accept YAML data, and return translated data."""

    def _translate_yaml_data(data):
        if isinstance(data, list):
            for item in data:
                _translate_yaml_data(item)
        elif isinstance(data, dict):
            for key, value in data.items():
                _translate_yaml_data(value)
                text = text_to_translate(value, key in keys)
                if text:
                    data[key] = translator.gettext(text)
                    for old, new in kwargs.items():
                        data[key] = data[key].replace("{{" + old + "}}", new)

    data = deepcopy(source)
    _translate_yaml_data(data)
    return data
