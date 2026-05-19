import unittest

from app.services.node_service import NodeService
from app.services.pod_service import PodService
from app.utils.resource_parser import calculate_gpu_requests_limits
from tests.fixtures.kubernetes_objects import FakeCoreV1, fixture_pod


class KubernetesNormalizationTest(unittest.TestCase):
    def setUp(self):
        self.core = FakeCoreV1()

    def test_node_normalization_includes_required_fields_and_gpu(self):
        node = NodeService(core_v1=self.core).get_node("local", "gpu-worker-01")
        data = node.dict(by_alias=True)

        self.assertEqual(data["name"], "gpu-worker-01")
        self.assertEqual(data["status"], "Ready")
        self.assertIn("gpu", data["roles"])
        self.assertEqual(data["kubeletVersion"], "v1.30.0")
        self.assertEqual(data["osImage"], "Ubuntu 22.04 LTS")
        self.assertEqual(data["containerRuntimeVersion"], "containerd://1.7.0")
        self.assertEqual(data["capacity"]["gpu"], 8)
        self.assertEqual(data["allocatable"]["gpu"], 8)
        self.assertEqual(data["conditions"][0]["type"], "Ready")

    def test_pod_normalization_includes_required_fields_and_gpu(self):
        pod = PodService(core_v1=self.core).get_pod("local", "ml", "training-job-h100")
        data = pod.dict(by_alias=True)

        self.assertEqual(data["namespace"], "ml")
        self.assertEqual(data["name"], "training-job-h100")
        self.assertEqual(data["phase"], "Running")
        self.assertEqual(data["nodeName"], "gpu-worker-01")
        self.assertEqual(data["podIP"], "10.244.1.10")
        self.assertEqual(data["hostIP"], "10.0.0.11")
        self.assertEqual(data["restartCount"], 2)
        self.assertEqual(data["labels"]["dataiku.com/job"], "true")
        self.assertEqual(data["resourceRequests"]["nvidia.com/gpu"], "1")
        self.assertEqual(data["resourceLimits"]["nvidia.com/gpu"], "1")
        self.assertEqual(data["gpuRequests"], 1)
        self.assertEqual(data["gpuLimits"], 1)
        self.assertEqual(data["containers"][0]["gpuRequests"], 1)

    def test_pod_filters_status_node_and_gpu_only(self):
        service = PodService(core_v1=self.core)

        self.assertEqual(len(service.list_pods("local", status="Running")), 1)
        self.assertEqual(len(service.list_pods("local", node_name="gpu-worker-01")), 1)
        self.assertEqual(len(service.list_pods("local", gpu_only=True)), 2)

    def test_gpu_utility_sums_container_requests_and_limits(self):
        pod = fixture_pod()
        requests, limits = calculate_gpu_requests_limits(pod.spec.containers)
        self.assertEqual(requests, 1)
        self.assertEqual(limits, 1)


if __name__ == "__main__":
    unittest.main()
