from fastapi import HTTPException

from app.schemas.cluster import ClusterOverview, GpuSummary, StatusCount
from app.services.kubernetes_client import KubernetesClientError, KubernetesClientFactory
from app.utils.kubernetes_object import obj_get
from app.utils.resource_parser import GPU_RESOURCE_NAME, calculate_gpu_requests_limits, parse_int_resource


class ClusterService:
    """ReadOnly cluster summary service backed by Kubernetes CoreV1/AppsV1 APIs."""

    def __init__(self, client_factory=None, core_v1=None, apps_v1=None):
        self.client_factory = client_factory or KubernetesClientFactory()
        self._core_v1 = core_v1
        self._apps_v1 = apps_v1

    def _clients(self):
        if self._core_v1 is not None and self._apps_v1 is not None:
            return self._core_v1, self._apps_v1
        clients = self.client_factory.create()
        return clients.core_v1, clients.apps_v1

    def get_overview(self, cluster_id):
        try:
            core_v1, apps_v1 = self._clients()
            nodes = obj_get(core_v1.list_node(), "items", [])
            namespaces = obj_get(core_v1.list_namespace(), "items", [])
            pods = obj_get(core_v1.list_pod_for_all_namespaces(), "items", [])
            services = obj_get(core_v1.list_service_for_all_namespaces(), "items", [])
            events = obj_get(core_v1.list_event_for_all_namespaces(), "items", [])
            deployments = obj_get(apps_v1.list_deployment_for_all_namespaces(), "items", [])

            return ClusterOverview(
                cluster_id=cluster_id,
                nodes=self._node_counts(nodes),
                namespaces=len(namespaces),
                pods=self._pod_counts(pods),
                deployments=len(deployments),
                services=len(services),
                warning_events=self._warning_event_count(events),
                gpu=self._gpu_summary(nodes, pods),
            )
        except KubernetesClientError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        except Exception as exc:
            raise self._http_error(exc, "failed to read Kubernetes cluster overview")

    def _http_error(self, exc, message):
        status = getattr(exc, "status", None)
        reason = getattr(exc, "reason", None) or str(exc)
        if status in (401, 403):
            return HTTPException(status_code=403, detail="{0}: Kubernetes RBAC denied access".format(message))
        return HTTPException(status_code=502, detail="{0}: {1}".format(message, reason))

    def _node_counts(self, nodes):
        running = 0
        for node in nodes:
            conditions = obj_get(obj_get(node, "status"), "conditions", []) or []
            ready = next((condition for condition in conditions if obj_get(condition, "type") == "Ready"), None)
            if ready is not None and obj_get(ready, "status") == "True":
                running += 1
        return StatusCount(total=len(nodes), running=running, unknown=max(len(nodes) - running, 0))

    def _pod_counts(self, pods):
        counts = {"Running": 0, "Pending": 0, "Failed": 0, "Succeeded": 0, "Unknown": 0}
        for pod in pods:
            phase = obj_get(obj_get(pod, "status"), "phase") or "Unknown"
            if phase not in counts:
                phase = "Unknown"
            counts[phase] += 1
        return StatusCount(
            total=len(pods),
            running=counts["Running"],
            pending=counts["Pending"],
            failed=counts["Failed"],
            succeeded=counts["Succeeded"],
            unknown=counts["Unknown"],
        )

    def _warning_event_count(self, events):
        return len([event for event in events if obj_get(event, "type") == "Warning"])

    def _gpu_summary(self, nodes, pods):
        gpu_nodes = 0
        total_gpu = 0
        for node in nodes:
            capacity = obj_get(obj_get(node, "status"), "capacity", {}) or {}
            node_gpu = parse_int_resource(capacity.get(GPU_RESOURCE_NAME))
            if node_gpu > 0:
                gpu_nodes += 1
                total_gpu += node_gpu

        requested_gpu = 0
        gpu_pods = 0
        for pod in pods:
            containers = obj_get(obj_get(pod, "spec"), "containers", []) or []
            requests, limits = calculate_gpu_requests_limits(containers)
            if requests > 0 or limits > 0:
                gpu_pods += 1
            requested_gpu += requests

        return GpuSummary(
            gpu_nodes=gpu_nodes,
            total_gpu=total_gpu,
            requested_gpu=requested_gpu,
            gpu_pods=gpu_pods,
        )
