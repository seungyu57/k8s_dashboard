from fastapi import HTTPException

from app.schemas.node import NodeCondition, NodeDetail, NodeResourceSummary, NodeSummary
from app.services.kubernetes_client import KubernetesClientError, KubernetesClientFactory
from app.utils.kubernetes_object import obj_get
from app.utils.resource_parser import GPU_RESOURCE_NAME, parse_int_resource


class NodeService:
    """ReadOnly Node service backed by the Kubernetes CoreV1 API."""

    def __init__(self, client_factory=None, core_v1=None):
        self.client_factory = client_factory or KubernetesClientFactory()
        self._core_v1 = core_v1

    def _core(self):
        if self._core_v1 is not None:
            return self._core_v1
        return self.client_factory.create().core_v1

    def list_nodes(self, cluster_id):
        try:
            response = self._core().list_node()
            return [self._normalize_node(node, detail=False) for node in obj_get(response, "items", [])]
        except KubernetesClientError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        except Exception as exc:
            raise self._http_error(exc, "failed to list Kubernetes nodes")

    def get_node(self, cluster_id, node_name):
        try:
            node = self._core().read_node(name=node_name)
            return self._normalize_node(node, detail=True)
        except KubernetesClientError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        except Exception as exc:
            raise self._http_error(exc, "failed to read Kubernetes node '{0}'".format(node_name))

    def _http_error(self, exc, message):
        status = getattr(exc, "status", None)
        reason = getattr(exc, "reason", None) or str(exc)
        if status == 404:
            return HTTPException(status_code=404, detail="{0}: not found".format(message))
        if status in (401, 403):
            return HTTPException(status_code=403, detail="{0}: Kubernetes RBAC denied access".format(message))
        return HTTPException(status_code=502, detail="{0}: {1}".format(message, reason))

    def _normalize_node(self, node, detail=False):
        metadata = obj_get(node, "metadata")
        status = obj_get(node, "status")
        node_info = obj_get(status, "node_info")
        labels = obj_get(metadata, "labels", {}) or {}
        annotations = obj_get(metadata, "annotations", {}) or {}
        capacity = obj_get(status, "capacity", {}) or {}
        allocatable = obj_get(status, "allocatable", {}) or {}
        conditions = [self._normalize_condition(c) for c in obj_get(status, "conditions", []) or []]

        ready = next((c for c in conditions if c.type == "Ready"), None)
        node_status = "Ready" if ready and ready.status == "True" else "NotReady"

        data = {
            "name": obj_get(metadata, "name"),
            "status": node_status,
            "roles": self._roles_from_labels(labels),
            "kubelet_version": obj_get(node_info, "kubelet_version"),
            "os_image": obj_get(node_info, "os_image"),
            "container_runtime_version": obj_get(node_info, "container_runtime_version"),
            "capacity": self._normalize_resources(capacity),
            "allocatable": self._normalize_resources(allocatable),
            "conditions": conditions,
        }
        if detail:
            data.update({"labels": labels, "annotations": annotations, "pods": []})
            return NodeDetail(**data)
        return NodeSummary(**data)

    def _normalize_condition(self, condition):
        return NodeCondition(
            type=obj_get(condition, "type"),
            status=obj_get(condition, "status"),
            reason=obj_get(condition, "reason"),
            message=obj_get(condition, "message"),
        )

    def _normalize_resources(self, resources):
        return NodeResourceSummary(
            cpu=str(resources.get("cpu")) if resources.get("cpu") is not None else None,
            memory=str(resources.get("memory")) if resources.get("memory") is not None else None,
            gpu=parse_int_resource(resources.get(GPU_RESOURCE_NAME)),
        )

    def _roles_from_labels(self, labels):
        roles = []
        for key, value in labels.items():
            prefix = "node-role.kubernetes.io/"
            if key.startswith(prefix):
                role = key[len(prefix):] or value or "unknown"
                roles.append(role)
        if not roles:
            roles.append("worker")
        if labels.get("nvidia.com/gpu.present") == "true" and "gpu" not in roles:
            roles.append("gpu")
        return sorted(roles)
