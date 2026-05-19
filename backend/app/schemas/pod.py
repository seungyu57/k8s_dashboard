from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ApiModel(BaseModel):
    class Config:
        allow_population_by_field_name = True


class ContainerResource(ApiModel):
    name: str
    requests: Dict[str, str] = Field(default_factory=dict)
    limits: Dict[str, str] = Field(default_factory=dict)
    gpu_requests: int = Field(0, alias="gpuRequests")
    gpu_limits: int = Field(0, alias="gpuLimits")
    restart_count: int = Field(0, alias="restartCount")
    ready: bool = False
    state: Optional[str] = None
    reason: Optional[str] = None


class PodSummary(ApiModel):
    namespace: str
    name: str
    phase: str
    node_name: Optional[str] = Field(None, alias="nodeName")
    pod_ip: Optional[str] = Field(None, alias="podIP")
    host_ip: Optional[str] = Field(None, alias="hostIP")
    restart_count: int = Field(0, alias="restartCount")
    created_at: Optional[str] = Field(None, alias="createdAt")
    labels: Dict[str, str] = Field(default_factory=dict)
    containers: List[ContainerResource]
    waiting_reason: Optional[str] = Field(None, alias="waitingReason")
    resource_requests: Dict[str, str] = Field(default_factory=dict, alias="resourceRequests")
    resource_limits: Dict[str, str] = Field(default_factory=dict, alias="resourceLimits")
    gpu_requests: int = Field(0, alias="gpuRequests")
    gpu_limits: int = Field(0, alias="gpuLimits")


class PodDetail(PodSummary):
    annotations: Dict[str, str] = Field(default_factory=dict)
    conditions: List[Dict] = Field(default_factory=list)
    events: List[Dict] = Field(default_factory=list)
