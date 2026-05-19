from fastapi import APIRouter

from app.schemas.cluster import ClusterOverview
from app.services.cluster_service import ClusterService

router = APIRouter()
service = ClusterService()


@router.get("/clusters/local/overview", response_model=ClusterOverview)
def local_cluster_overview():
    return service.get_overview("local")
