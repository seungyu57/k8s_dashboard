from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ApiModel(BaseModel):
    class Config:
        allow_population_by_field_name = True


class NodeCondition(ApiModel):
    type: str
    status: str
    reason: Optional[str] = None
    message: Optional[str] = None


class NodeResourceSummary(ApiModel):
    cpu: Optional[str] = None
    memory: Optional[str] = None
    gpu: int = 0


class NodeSummary(ApiModel):
    name: str
    status: str
    roles: List[str]
    kubelet_version: Optional[str] = Field(None, alias="kubeletVersion")
    os_image: Optional[str] = Field(None, alias="osImage")
    container_runtime_version: Optional[str] = Field(None, alias="containerRuntimeVersion")
    capacity: NodeResourceSummary
    allocatable: NodeResourceSummary
    conditions: List[NodeCondition] = Field(default_factory=list)


class NodeDetail(NodeSummary):
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)
    pods: List[Dict] = Field(default_factory=list)
