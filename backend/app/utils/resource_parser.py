GPU_RESOURCE_NAME = "nvidia.com/gpu"


def parse_int_resource(value):
    """Parse integer Kubernetes extended resources such as nvidia.com/gpu."""
    if value is None:
        return 0
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def gpu_count(resources):
    if not resources:
        return 0
    return parse_int_resource(resources.get(GPU_RESOURCE_NAME))


def calculate_gpu_requests_limits(containers):
    """Return total nvidia.com/gpu requests and limits across containers.

    containers may be Kubernetes client objects, SimpleNamespace fixtures, or dicts.
    """
    from app.utils.kubernetes_object import obj_get

    requests = 0
    limits = 0
    for container in containers or []:
        resources = obj_get(container, "resources", None)
        container_requests = obj_get(resources, "requests", {}) or {}
        container_limits = obj_get(resources, "limits", {}) or {}
        requests += gpu_count(container_requests)
        limits += gpu_count(container_limits)
    return requests, limits
