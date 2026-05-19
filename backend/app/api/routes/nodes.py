from typing import List

from fastapi import APIRouter

from app.schemas.node import NodeDetail, NodeSummary
from app.services.node_service import NodeService

router = APIRouter()
service = NodeService()


@router.get("/clusters/{cluster_id}/nodes", response_model=List[NodeSummary])
def list_nodes(cluster_id):
    return service.list_nodes(cluster_id)


@router.get("/clusters/{cluster_id}/nodes/{nodeName}", response_model=NodeDetail)
def get_node(cluster_id, nodeName):
    return service.get_node(cluster_id, nodeName)
