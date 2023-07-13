def to_str(obj):
    if obj in [None, True, False, []]:
        return obj
    else:
        return str(obj)

def truncate(text: str, max: int, extension: str="…"):
    if len(text) > max:
        return text[:max-1]+extension
    else: return text
