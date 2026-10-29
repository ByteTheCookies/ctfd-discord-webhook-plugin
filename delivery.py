"""Best-effort Discord delivery with a fixed queue and one sender per worker process."""

import copy
import logging
import queue
import threading

import requests

log = logging.getLogger(__name__)


class BoundedSender:
    def __init__(self, capacity=128):
        self.pending = queue.Queue(maxsize=capacity)
        self.lock = threading.Lock()
        self.worker = None

    def enqueue(self, webhook):
        """Never wait for Discord, queue space, or a previous notification."""
        try:
            item = (webhook.url, copy.deepcopy(webhook.json), webhook.proxies)
            with self.lock:
                if self.worker is None or not self.worker.is_alive():
                    self.worker = threading.Thread(target=self._run, daemon=True)
                    self.worker.start()
            self.pending.put_nowait(item)
            return True
        except queue.Full:
            log.warning("Discord notification queue full; notification dropped")
        except Exception as exc:
            # Exception text can contain the webhook URL/token: log its type only.
            log.warning("Discord notification enqueue failed (%s)", type(exc).__name__)
        return False

    def _run(self):
        while True:
            item = self.pending.get()
            try:
                self._deliver(item)
            finally:
                self.pending.task_done()

    @staticmethod
    def _deliver(item):
        url, payload, proxies = item
        try:
            # Do not consume response bodies, follow redirects, retry, or use the
            # old discord-webhook.execute(), whose transport has no timeout.
            with requests.post(
                url, json=payload, proxies=proxies, timeout=(3.05, 5),
                allow_redirects=False, stream=True,
            ) as response:
                response.raise_for_status()
                if response.status_code != 204:
                    log.warning("Discord notification returned HTTP %s", response.status_code)
        except Exception as exc:
            log.warning("Discord notification delivery failed (%s)", type(exc).__name__)


# Lazy thread creation avoids starting a background thread before Gunicorn forks.
sender = BoundedSender()
