import unittest

from app.services.cluster_service import ClusterService
from tests.fixtures.kubernetes_objects import FakeAppsV1, FakeCoreV1


class ClusterOverviewTest(unittest.TestCase):
    def test_overview_uses_kubernetes_api_counts_and_gpu_summary(self):
        overview = ClusterService(core_v1=FakeCoreV1(), apps_v1=FakeAppsV1()).get_overview("local")
        data = overview.dict()

        self.assertEqual(data["cluster_id"], "local")
        self.assertEqual(data["nodes"]["total"], 1)
        self.assertEqual(data["nodes"]["running"], 1)
        self.assertEqual(data["namespaces"], 2)
        self.assertEqual(data["pods"]["total"], 2)
        self.assertEqual(data["pods"]["running"], 1)
        self.assertEqual(data["pods"]["pending"], 1)
        self.assertEqual(data["deployments"], 1)
        self.assertEqual(data["services"], 1)
        self.assertEqual(data["warning_events"], 1)
        self.assertEqual(data["gpu"]["gpu_nodes"], 1)
        self.assertEqual(data["gpu"]["total_gpu"], 8)
        self.assertEqual(data["gpu"]["requested_gpu"], 2)
        self.assertEqual(data["gpu"]["gpu_pods"], 2)


if __name__ == "__main__":
    unittest.main()
