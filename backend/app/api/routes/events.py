from typing import List

from fastapi import APIRouter

from app.schemas.event import EventSummary
from app.services.event_service import EventService

router = APIRouter()
service = EventService()


@router.get("/clusters/{cluster_id}/events", response_model=List[EventSummary])
def list_events(cluster_id, namespace=None, type=None, reason=None, involvedKind=None, involvedName=None):
    return service.list_events(
        cluster_id,
        namespace=namespace,
        event_type=type,
        reason=reason,
        involved_kind=involvedKind,
        involved_name=involvedName,
    )


@router.get("/clusters/{cluster_id}/namespaces/{namespace}/pods/{podName}/events", response_model=List[EventSummary])
def list_pod_events(cluster_id, namespace, podName):
    return service.list_pod_events(cluster_id, namespace, podName)
