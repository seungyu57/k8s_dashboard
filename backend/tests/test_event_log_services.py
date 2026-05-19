import unittest

from app.services.event_service import EventService
from app.services.log_service import LogService
from tests.fixtures.kubernetes_objects import FakeCoreV1


class EventLogServiceTest(unittest.TestCase):
    def setUp(self):
        self.core = FakeCoreV1()

    def test_list_pod_events_filters_involved_pod(self):
        events = EventService(core_v1=self.core).list_pod_events("local", "ml", "training-job-h100")
        self.assertEqual(len(events), 1)
        data = events[0].dict(by_alias=True)
        self.assertEqual(data["namespace"], "ml")
        self.assertEqual(data["type"], "Normal")
        self.assertEqual(data["reason"], "Scheduled")
        self.assertEqual(data["involvedKind"], "Pod")
        self.assertEqual(data["involvedName"], "training-job-h100")
        self.assertIn("2026-05-19T00:10:01", data["lastTimestamp"])

    def test_list_events_supports_warning_filter(self):
        events = EventService(core_v1=self.core).list_events("local", namespace="ml", event_type="Warning")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].reason, "FailedScheduling")

    def test_get_pod_logs_uses_tail_limit_and_kubernetes_log_api(self):
        logs = LogService(core_v1=self.core).get_pod_logs("local", "ml", "training-job-h100", "trainer", 999999)
        data = logs.dict(by_alias=True)
        self.assertEqual(data["namespace"], "ml")
        self.assertEqual(data["pod"], "training-job-h100")
        self.assertEqual(data["container"], "trainer")
        self.assertEqual(data["tailLines"], 2000)
        self.assertIn("trainer started", data["logs"])
        self.assertEqual(self.core.last_log_call["tail_lines"], 2000)
        self.assertTrue(self.core.last_log_call["timestamps"])


if __name__ == "__main__":
    unittest.main()
