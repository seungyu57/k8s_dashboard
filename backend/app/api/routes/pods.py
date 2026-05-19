from typing import List, Optional

from fastapi import APIRouter

from app.schemas.pod import PodDetail, PodSummary
from app.services.pod_service import PodService

router = APIRouter()
service = PodService()


@router.get("/clusters/{cluster_id}/pods", response_model=List[PodSummary])
def list_pods(cluster_id, namespace: Optional[str] = None, status: Optional[str] = None, nodeName: Optional[str] = None, gpuOnly: bool = False, search: Optional[str] = None, dataikuOnly: bool = False):
    return service.list_pods(cluster_id, namespace=namespace, status=status, node_name=nodeName, gpu_only=gpuOnly, search=search, dataiku_only=dataikuOnly)


@router.get("/clusters/{cluster_id}/namespaces/{namespace}/pods/{podName}", response_model=PodDetail)
def get_pod(cluster_id: str, namespace: str, podName: str):
    return service.get_pod(cluster_id, namespace, podName)
