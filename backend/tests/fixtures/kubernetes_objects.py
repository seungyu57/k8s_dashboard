from datetime import datetime
from types import SimpleNamespace as NS


def fixture_node():
    return NS(
        metadata=NS(
            name="gpu-worker-01",
            labels={
                "node-role.kubernetes.io/worker": "",
                "nvidia.com/gpu.present": "true",
            },
            annotations={"example": "annotation"},
        ),
        status=NS(
            capacity={"cpu": "64", "memory": "512Gi", "nvidia.com/gpu": "8"},
            allocatable={"cpu": "62000m", "memory": "500Gi", "nvidia.com/gpu": "8"},
            conditions=[NS(type="Ready", status="True", reason="KubeletReady", message="kubelet is posting ready status")],
            node_info=NS(
                kubelet_version="v1.30.0",
                os_image="Ubuntu 22.04 LTS",
                container_runtime_version="containerd://1.7.0",
            ),
        ),
    )


def fixture_pod():
    return NS(
        metadata=NS(
            namespace="ml",
            name="training-job-h100",
            creation_timestamp=datetime(2026, 5, 19, 0, 10, 0),
            labels={"app": "trainer", "dataiku.com/job": "true"},
            annotations={"owner": "mlops"},
        ),
        spec=NS(
            node_name="gpu-worker-01",
            containers=[
                NS(
                    name="trainer",
                    resources=NS(
                        requests={"cpu": "4", "memory": "32Gi", "nvidia.com/gpu": "1"},
                        limits={"memory": "64Gi", "nvidia.com/gpu": "1"},
                    ),
                )
            ],
        ),
        status=NS(
            phase="Running",
            pod_ip="10.244.1.10",
            host_ip="10.0.0.11",
            container_statuses=[
                NS(
                    name="trainer",
                    restart_count=2,
                    ready=True,
                    state=NS(running=NS(started_at=datetime(2026, 5, 19, 0, 11, 0))),
                )
            ],
            conditions=[NS(type="Ready", status="True", reason=None, message=None)],
        ),
    )


def fixture_pending_pod():
    return NS(
        metadata=NS(
            namespace="ml",
            name="queued-gpu-job",
            creation_timestamp=datetime(2026, 5, 19, 0, 12, 0),
            labels={"app": "trainer"},
            annotations={},
        ),
        spec=NS(
            node_name=None,
            containers=[
                NS(
                    name="trainer",
                    resources=NS(
                        requests={"nvidia.com/gpu": "1"},
                        limits={"nvidia.com/gpu": "1"},
                    ),
                )
            ],
        ),
        status=NS(
            phase="Pending",
            pod_ip=None,
            host_ip=None,
            container_statuses=[
                NS(
                    name="trainer",
                    restart_count=0,
                    ready=False,
                    state=NS(waiting=NS(reason="Unschedulable")),
                )
            ],
            conditions=[],
        ),
    )


def fixture_events():
    return [
        NS(
            metadata=NS(namespace="ml"),
            type="Normal",
            reason="Scheduled",
            message="Successfully assigned ml/training-job-h100 to gpu-worker-01",
            involved_object=NS(kind="Pod", name="training-job-h100"),
            count=1,
            first_timestamp=datetime(2026, 5, 19, 0, 10, 1),
            last_timestamp=datetime(2026, 5, 19, 0, 10, 1),
        ),
        NS(
            metadata=NS(namespace="ml"),
            type="Warning",
            reason="FailedScheduling",
            message="0/2 nodes are available: insufficient nvidia.com/gpu",
            involved_object=NS(kind="Pod", name="queued-gpu-job"),
            count=3,
            first_timestamp=datetime(2026, 5, 19, 0, 12, 0),
            last_timestamp=datetime(2026, 5, 19, 0, 12, 30),
        ),
    ]


class FakeListResponse:
    def __init__(self, items):
        self.items = items


class FakeCoreV1:
    def __init__(self):
        self.node = fixture_node()
        self.pods = [fixture_pod(), fixture_pending_pod()]
        self.events = fixture_events()
        self.namespaces = [NS(metadata=NS(name="default")), NS(metadata=NS(name="ml"))]
        self.services = [NS(metadata=NS(namespace="default", name="kubernetes"))]
        self.last_log_call = None

    def list_node(self):
        return FakeListResponse([self.node])

    def read_node(self, name):
        return self.node

    def list_namespace(self):
        return FakeListResponse(self.namespaces)

    def list_service_for_all_namespaces(self):
        return FakeListResponse(self.services)

    def list_pod_for_all_namespaces(self):
        return FakeListResponse(self.pods)

    def list_namespaced_pod(self, namespace):
        return FakeListResponse([pod for pod in self.pods if pod.metadata.namespace == namespace])

    def read_namespaced_pod(self, name, namespace):
        for pod in self.pods:
            if pod.metadata.namespace == namespace and pod.metadata.name == name:
                return pod
        raise RuntimeError("not found")

    def list_event_for_all_namespaces(self):
        return FakeListResponse(self.events)

    def list_namespaced_event(self, namespace):
        return FakeListResponse([event for event in self.events if event.metadata.namespace == namespace])

    def read_namespaced_pod_log(self, name, namespace, container=None, tail_lines=None, timestamps=True):
        self.last_log_call = {
            "name": name,
            "namespace": namespace,
            "container": container,
            "tail_lines": tail_lines,
            "timestamps": timestamps,
        }
        return "2026-05-19T00:11:00Z trainer started\n2026-05-19T00:11:01Z loading data"


class FakeAppsV1:
    def __init__(self):
        self.deployments = [NS(metadata=NS(namespace="ml", name="trainer"))]

    def list_deployment_for_all_namespaces(self):
        return FakeListResponse(self.deployments)
