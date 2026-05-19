from fastapi import HTTPException

from app.schemas.pod import ContainerResource, PodDetail, PodSummary
from app.services.kubernetes_client import KubernetesClientError, KubernetesClientFactory
from app.utils.kubernetes_object import isoformat_or_none, obj_get
from app.utils.resource_parser import calculate_gpu_requests_limits, gpu_count


class PodService:
    """ReadOnly Pod service backed by the Kubernetes CoreV1 API."""

    def __init__(self, client_factory=None, core_v1=None):
        self.client_factory = client_factory or KubernetesClientFactory()
        self._core_v1 = core_v1

    def _core(self):
        if self._core_v1 is not None:
            return self._core_v1
        return self.client_factory.create().core_v1

    def list_pods(self, cluster_id, namespace=None, status=None, node_name=None, gpu_only=False, search=None, dataiku_only=False):
        try:
            if namespace:
                response = self._core().list_namespaced_pod(namespace=namespace)
            else:
                response = self._core().list_pod_for_all_namespaces()
            pods = [self._normalize_pod(pod, detail=False) for pod in obj_get(response, "items", [])]
            if status:
                pods = [pod for pod in pods if pod.phase and pod.phase.lower() == status.lower()]
            if node_name:
                pods = [pod for pod in pods if pod.node_name == node_name]
            if gpu_only:
                pods = [pod for pod in pods if pod.gpu_requests > 0 or pod.gpu_limits > 0]
            if dataiku_only:
                pods = [pod for pod in pods if self._is_dataiku_pod(pod)]
            if search:
                lowered = search.lower()
                pods = [pod for pod in pods if self._matches_search(pod, lowered)]
            return pods
        except KubernetesClientError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        except Exception as exc:
            raise self._http_error(exc, "failed to list Kubernetes pods")

    def get_pod(self, cluster_id, namespace, pod_name):
        try:
            pod = self._core().read_namespaced_pod(name=pod_name, namespace=namespace)
            return self._normalize_pod(pod, detail=True)
        except KubernetesClientError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        except Exception as exc:
            raise self._http_error(exc, "failed to read Kubernetes pod '{0}/{1}'".format(namespace, pod_name))

    def _http_error(self, exc, message):
        status = getattr(exc, "status", None)
        reason = getattr(exc, "reason", None) or str(exc)
        if status == 404:
            return HTTPException(status_code=404, detail="{0}: not found".format(message))
        if status in (401, 403):
            return HTTPException(status_code=403, detail="{0}: Kubernetes RBAC denied access".format(message))
        return HTTPException(status_code=502, detail="{0}: {1}".format(message, reason))

    def _normalize_pod(self, pod, detail=False):
        metadata = obj_get(pod, "metadata")
        spec = obj_get(pod, "spec")
        status = obj_get(pod, "status")
        containers = obj_get(spec, "containers", []) or []
        container_statuses = obj_get(status, "container_statuses", []) or []
        status_by_name = {obj_get(s, "name"): s for s in container_statuses}

        normalized_containers = []
        resource_requests = {}
        resource_limits = {}
        restart_count = 0
        waiting_reason = None

        for container in containers:
            name = obj_get(container, "name")
            resources = obj_get(container, "resources")
            requests = dict(obj_get(resources, "requests", {}) or {})
            limits = dict(obj_get(resources, "limits", {}) or {})
            status_obj = status_by_name.get(name)
            container_restart_count = obj_get(status_obj, "restart_count", 0) or 0
            restart_count += container_restart_count
            state, reason = self._container_state(status_obj)
            if reason and waiting_reason is None:
                waiting_reason = reason
            container_gpu_requests = gpu_count(requests)
            container_gpu_limits = gpu_count(limits)
            normalized_containers.append(
                ContainerResource(
                    name=name,
                    requests=requests,
                    limits=limits,
                    gpu_requests=container_gpu_requests,
                    gpu_limits=container_gpu_limits,
                    restart_count=container_restart_count,
                    ready=bool(obj_get(status_obj, "ready", False)),
                    state=state,
                    reason=reason,
                )
            )
            self._merge_resources(resource_requests, requests)
            self._merge_resources(resource_limits, limits)

        gpu_requests, gpu_limits = calculate_gpu_requests_limits(containers)
        data = {
            "namespace": obj_get(metadata, "namespace"),
            "name": obj_get(metadata, "name"),
            "phase": obj_get(status, "phase"),
            "node_name": obj_get(spec, "node_name"),
            "pod_ip": obj_get(status, "pod_ip"),
            "host_ip": obj_get(status, "host_ip"),
            "restart_count": restart_count,
            "created_at": isoformat_or_none(obj_get(metadata, "creation_timestamp")),
            "labels": obj_get(metadata, "labels", {}) or {},
            "containers": normalized_containers,
            "waiting_reason": waiting_reason,
            "resource_requests": resource_requests,
            "resource_limits": resource_limits,
            "gpu_requests": gpu_requests,
            "gpu_limits": gpu_limits,
        }
        if detail:
            data.update({
                "annotations": obj_get(metadata, "annotations", {}) or {},
                "conditions": [self._condition_dict(c) for c in obj_get(status, "conditions", []) or []],
                "events": [],
            })
            return PodDetail(**data)
        return PodSummary(**data)

    def _container_state(self, container_status):
        state_obj = obj_get(container_status, "state")
        if state_obj is None:
            return None, None
        for state_name in ("waiting", "running", "terminated"):
            detail = obj_get(state_obj, state_name)
            if detail is not None:
                return state_name, obj_get(detail, "reason")
        return None, None

    def _merge_resources(self, target, source):
        for key, value in (source or {}).items():
            if key not in target:
                target[key] = str(value)
            elif target[key] != str(value):
                target[key] = "{0} + {1}".format(target[key], value)

    def _is_dataiku_pod(self, pod):
        return any(key.startswith("dataiku.com/") for key in (pod.labels or {}).keys())

    def _matches_search(self, pod, lowered):
        values = [pod.namespace, pod.name, pod.node_name or "", pod.phase or "", pod.waiting_reason or ""]
        labels = pod.labels or {}
        dataiku_keys = [
            "dataiku.com/dku-project-key",
            "dataiku.com/dku-exec-submitter",
            "dataiku.com/dku-execution-id",
            "dataiku.com/dku-container-conf",
            "dataiku.com/dku-execution-type",
        ]
        values.extend(labels.get(key, "") for key in dataiku_keys)
        return any(lowered in str(value).lower() for value in values if value is not None)

    def _condition_dict(self, condition):
        return {
            "type": obj_get(condition, "type"),
            "status": obj_get(condition, "status"),
            "reason": obj_get(condition, "reason"),
            "message": obj_get(condition, "message"),
        }
