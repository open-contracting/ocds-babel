def text_to_translate(value, condition=True):  # noqa: FBT002
    if condition and isinstance(value, str):
        return value.strip()
    return None
