from typing import List

from fastapi import APIRouter

from app.schemas.pod import PodDetail, PodSummary
from app.services.pod_service import PodService

router = APIRouter()
service = PodService()


@router.get("/clusters/{cluster_id}/pods", response_model=List[PodSummary])
def list_pods(cluster_id, namespace=None, status=None, nodeName=None, gpuOnly=False):
    return service.list_pods(cluster_id, namespace=namespace, status=status, node_name=nodeName, gpu_only=gpuOnly)


@router.get("/clusters/{cluster_id}/namespaces/{namespace}/pods/{podName}", response_model=PodDetail)
def get_pod(cluster_id, namespace, podName):
    return service.get_pod(cluster_id, namespace, podName)
