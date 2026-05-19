from fastapi import HTTPException

from app.schemas.event import EventSummary
from app.services.kubernetes_client import KubernetesClientError, KubernetesClientFactory
from app.utils.kubernetes_object import isoformat_or_none, obj_get


class EventService:
    """ReadOnly Event service backed by the Kubernetes CoreV1 API."""

    def __init__(self, client_factory=None, core_v1=None):
        self.client_factory = client_factory or KubernetesClientFactory()
        self._core_v1 = core_v1

    def _core(self):
        if self._core_v1 is not None:
            return self._core_v1
        return self.client_factory.create().core_v1

    def list_events(self, cluster_id, namespace=None, event_type=None, reason=None, involved_kind=None, involved_name=None):
        try:
            if namespace:
                response = self._core().list_namespaced_event(namespace=namespace)
            else:
                response = self._core().list_event_for_all_namespaces()
            events = [self._normalize_event(event) for event in obj_get(response, "items", [])]
            if event_type:
                events = [event for event in events if (event.type or "").lower() == event_type.lower()]
            if reason:
                events = [event for event in events if (event.reason or "").lower() == reason.lower()]
            if involved_kind:
                events = [event for event in events if (event.involved_kind or "").lower() == involved_kind.lower()]
            if involved_name:
                events = [event for event in events if event.involved_name == involved_name]
            return events
        except KubernetesClientError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        except Exception as exc:
            raise self._http_error(exc, "failed to list Kubernetes events")

    def list_pod_events(self, cluster_id, namespace, pod_name):
        return self.list_events(cluster_id, namespace=namespace, involved_kind="Pod", involved_name=pod_name)

    def _http_error(self, exc, message):
        status = getattr(exc, "status", None)
        reason = getattr(exc, "reason", None) or str(exc)
        if status == 404:
            return HTTPException(status_code=404, detail="{0}: not found".format(message))
        if status in (401, 403):
            return HTTPException(status_code=403, detail="{0}: Kubernetes RBAC denied access".format(message))
        return HTTPException(status_code=502, detail="{0}: {1}".format(message, reason))

    def _normalize_event(self, event):
        metadata = obj_get(event, "metadata")
        involved = obj_get(event, "involved_object") or obj_get(event, "regarding")
        first_timestamp = (
            obj_get(event, "first_timestamp")
            or obj_get(event, "event_time")
            or obj_get(event, "deprecated_first_timestamp")
        )
        last_timestamp = (
            obj_get(event, "last_timestamp")
            or obj_get(event, "event_time")
            or obj_get(event, "deprecated_last_timestamp")
        )
        return EventSummary(
            namespace=obj_get(metadata, "namespace"),
            type=obj_get(event, "type"),
            reason=obj_get(event, "reason"),
            message=obj_get(event, "message"),
            involved_kind=obj_get(involved, "kind"),
            involved_name=obj_get(involved, "name"),
            count=obj_get(event, "count") or obj_get(event, "deprecated_count"),
            first_timestamp=isoformat_or_none(first_timestamp),
            last_timestamp=isoformat_or_none(last_timestamp),
        )
