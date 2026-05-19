from pydantic import BaseModel


class StatusCount(BaseModel):
    total: int
    running: int = 0
    pending: int = 0
    failed: int = 0
    succeeded: int = 0
    unknown: int = 0


class GpuSummary(BaseModel):
    gpu_nodes: int
    total_gpu: int
    requested_gpu: int
    gpu_pods: int


class ClusterOverview(BaseModel):
    cluster_id: str
    nodes: StatusCount
    namespaces: int
    pods: StatusCount
    deployments: int
    services: int
    warning_events: int
    gpu: GpuSummary
