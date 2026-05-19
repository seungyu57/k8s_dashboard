import unittest

from app.core.config import get_settings
from app.services.cluster_service import ClusterService
from app.services.kubernetes_client import KubernetesClientFactory


class MockModeTest(unittest.TestCase):
    def test_factory_returns_mock_clients_when_enabled(self):
        settings = get_settings()
        previous = settings.k8s_mock_mode
        settings.k8s_mock_mode = True
        try:
            clients = KubernetesClientFactory().create()
            overview = ClusterService(core_v1=clients.core_v1, apps_v1=clients.apps_v1).get_overview("local")
            self.assertEqual(overview.nodes.total, 2)
            self.assertEqual(overview.gpu.total_gpu, 8)
            self.assertGreaterEqual(overview.pods.total, 3)
        finally:
            settings.k8s_mock_mode = previous


if __name__ == "__main__":
    unittest.main()
