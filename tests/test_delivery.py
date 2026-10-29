import importlib.util
from pathlib import Path
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("delivery", Path(__file__).parents[1] / "delivery.py")
delivery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delivery)


class DeliveryTests(unittest.TestCase):
    def test_timeout_and_payload_without_unbounded_execute(self):
        response = unittest.mock.MagicMock()
        response.__enter__.return_value.status_code = 204
        item = ("https://example.invalid/webhook", {"embeds": []}, None)
        with patch.object(delivery.requests, "post", return_value=response) as post:
            delivery.BoundedSender._deliver(item)
        self.assertEqual(post.call_args.kwargs["timeout"], (3.05, 5))
        self.assertFalse(post.call_args.kwargs["allow_redirects"])
        self.assertTrue(post.call_args.kwargs["stream"])
        self.assertEqual(post.call_args.kwargs["json"], {"embeds": []})

    def test_queue_remains_bounded_while_transport_is_stalled(self):
        entered, release = threading.Event(), threading.Event()
        sender = delivery.BoundedSender(capacity=2)

        def blocked(item):
            entered.set()
            release.wait(timeout=2)

        webhook = SimpleNamespace(url="https://example.invalid/webhook", json={}, proxies=None)
        with patch.object(sender, "_deliver", side_effect=blocked):
            self.assertTrue(sender.enqueue(webhook))
            self.assertTrue(entered.wait(timeout=1))
            thread = sender.worker
            self.assertTrue(sender.enqueue(webhook))
            self.assertTrue(sender.enqueue(webhook))
            self.assertFalse(sender.enqueue(webhook))
            self.assertIs(sender.worker, thread)
            release.set()
            sender.pending.join()

    def test_delivery_error_is_redacted_and_does_not_escape(self):
        with patch.object(delivery.requests, "post", side_effect=RuntimeError("secret URL")):
            with self.assertLogs(delivery.log, level="WARNING") as logs:
                delivery.BoundedSender._deliver(("unused", {}, None))
        self.assertNotIn("secret URL", " ".join(logs.output))
        self.assertIn("RuntimeError", " ".join(logs.output))


if __name__ == "__main__":
    unittest.main()
