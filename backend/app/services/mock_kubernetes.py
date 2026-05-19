from datetime import datetime
from types import SimpleNamespace as NS


class MockListResponse:
    def __init__(self, items):
        self.items = items


class MockCoreV1Api:
    """Small read-only Kubernetes API fixture for local UI development without kubeconfig."""

    def __init__(self):
        self.nodes = [
            self._node(
                name="control-plane-01",
                roles={"node-role.kubernetes.io/control-plane": ""},
                cpu="8",
                memory="32Gi",
                gpu="0",
            ),
            self._node(
                name="gpu-worker-01",
                roles={"node-role.kubernetes.io/worker": "", "nvidia.com/gpu.present": "true"},
                cpu="64",
                memory="512Gi",
                gpu="8",
            ),
        ]
        self.namespaces = [NS(metadata=NS(name="default")), NS(metadata=NS(name="ml")), NS(metadata=NS(name="dataiku"))]
        self.pods = [self._api_pod(), self._gpu_pod(), self._pending_gpu_pod()]
        self.events = self._events()
        self.services = [NS(metadata=NS(namespace="default", name="kubernetes")), NS(metadata=NS(namespace="ml", name="trainer-api"))]

    def list_node(self):
        return MockListResponse(self.nodes)

    def read_node(self, name):
        for node in self.nodes:
            if node.metadata.name == name:
                return node
        raise RuntimeError("node not found: {0}".format(name))

    def list_namespace(self):
        return MockListResponse(self.namespaces)

    def list_service_for_all_namespaces(self):
        return MockListResponse(self.services)

    def list_pod_for_all_namespaces(self):
        return MockListResponse(self.pods)

    def list_namespaced_pod(self, namespace):
        return MockListResponse([pod for pod in self.pods if pod.metadata.namespace == namespace])

    def read_namespaced_pod(self, name, namespace):
        for pod in self.pods:
            if pod.metadata.namespace == namespace and pod.metadata.name == name:
                return pod
        raise RuntimeError("pod not found: {0}/{1}".format(namespace, name))

    def list_event_for_all_namespaces(self):
        return MockListResponse(self.events)

    def list_namespaced_event(self, namespace):
        return MockListResponse([event for event in self.events if event.metadata.namespace == namespace])

    def read_namespaced_pod_log(self, name, namespace, container=None, tail_lines=None, timestamps=True):
        prefix = "2026-05-19T00:11:00Z " if timestamps else ""
        lines = [
            "{0}[mock] pod={1}/{2} container={3}".format(prefix, namespace, name, container or "default"),
            "{0}[mock] Kubernetes log API is running in K8S_MOCK_MODE".format(prefix),
            "{0}[mock] Set K8S_MOCK_MODE=false and KUBECONFIG to query a real cluster".format(prefix),
        ]
        return "\n".join(lines[-int(tail_lines or 500):])

    def _node(self, name, roles, cpu, memory, gpu):
        labels = {"kubernetes.io/hostname": name}
        labels.update(roles)
        capacity = {"cpu": cpu, "memory": memory}
        allocatable = {"cpu": cpu, "memory": memory}
        if int(gpu) > 0:
            capacity["nvidia.com/gpu"] = gpu
            allocatable["nvidia.com/gpu"] = gpu
        return NS(
            metadata=NS(name=name, labels=labels, annotations={}),
            status=NS(
                capacity=capacity,
                allocatable=allocatable,
                conditions=[NS(type="Ready", status="True", reason="KubeletReady", message="mock node ready")],
                node_info=NS(kubelet_version="v1.30.mock", os_image="Ubuntu 22.04 LTS", container_runtime_version="containerd://1.7.mock"),
            ),
        )

    def _api_pod(self):
        return self._pod("default", "api-server-demo", "Running", "control-plane-01", "10.244.0.10", "10.0.0.10", "api", {"cpu": "100m", "memory": "128Mi"}, {"cpu": "500m", "memory": "512Mi"})

    def _gpu_pod(self):
        return self._pod("ml", "training-job-h100", "Running", "gpu-worker-01", "10.244.1.10", "10.0.0.11", "trainer", {"cpu": "4", "memory": "32Gi", "nvidia.com/gpu": "1"}, {"memory": "64Gi", "nvidia.com/gpu": "1"}, labels={"app": "trainer", "dataiku.com/job": "true"})

    def _pending_gpu_pod(self):
        return self._pod("ml", "queued-gpu-job", "Pending", None, None, None, "trainer", {"nvidia.com/gpu": "1"}, {"nvidia.com/gpu": "1"}, waiting_reason="Unschedulable")

    def _pod(self, namespace, name, phase, node_name, pod_ip, host_ip, container_name, requests, limits, labels=None, waiting_reason=None):
        state = NS(waiting=NS(reason=waiting_reason)) if waiting_reason else NS(running=NS(started_at=datetime(2026, 5, 19, 0, 11, 0)))
        return NS(
            metadata=NS(namespace=namespace, name=name, creation_timestamp=datetime(2026, 5, 19, 0, 10, 0), labels=labels or {"app": name}, annotations={}),
            spec=NS(node_name=node_name, containers=[NS(name=container_name, resources=NS(requests=requests, limits=limits))]),
            status=NS(
                phase=phase,
                pod_ip=pod_ip,
                host_ip=host_ip,
                container_statuses=[NS(name=container_name, restart_count=0 if phase == "Pending" else 1, ready=phase == "Running", state=state)],
                conditions=[NS(type="Ready", status="True" if phase == "Running" else "False", reason=waiting_reason, message=None)],
            ),
        )

    def _events(self):
        return [
            NS(metadata=NS(namespace="ml"), type="Normal", reason="Scheduled", message="Successfully assigned ml/training-job-h100 to gpu-worker-01", involved_object=NS(kind="Pod", name="training-job-h100"), count=1, first_timestamp=datetime(2026, 5, 19, 0, 10, 1), last_timestamp=datetime(2026, 5, 19, 0, 10, 1)),
            NS(metadata=NS(namespace="ml"), type="Warning", reason="FailedScheduling", message="0/2 nodes are available: insufficient nvidia.com/gpu", involved_object=NS(kind="Pod", name="queued-gpu-job"), count=3, first_timestamp=datetime(2026, 5, 19, 0, 12, 0), last_timestamp=datetime(2026, 5, 19, 0, 12, 30)),
        ]


class MockAppsV1Api:
    def list_deployment_for_all_namespaces(self):
        return MockListResponse([NS(metadata=NS(namespace="ml", name="trainer")), NS(metadata=NS(namespace="dataiku", name="dss-exec"))])
