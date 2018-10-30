def text_to_translate(value, condition=True):
    if condition and isinstance(value, str):
        return value.strip()
