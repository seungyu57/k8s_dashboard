def obj_get(obj, name, default=None):
    """Read an attribute from Kubernetes client objects, dicts, or fixtures."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def metadata_name(obj):
    return obj_get(obj_get(obj, "metadata"), "name")


def isoformat_or_none(value):
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)
