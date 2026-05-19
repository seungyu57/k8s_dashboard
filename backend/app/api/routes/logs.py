from fastapi import APIRouter

from app.schemas.log import PodLogResponse
from app.services.log_service import LogService

router = APIRouter()
service = LogService()


@router.get("/clusters/{cluster_id}/namespaces/{namespace}/pods/{podName}/logs", response_model=PodLogResponse)
def get_pod_logs(cluster_id, namespace, podName, container=None, tailLines=None):
    return service.get_pod_logs(cluster_id, namespace, podName, container, tailLines)
