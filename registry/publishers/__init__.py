"""
registry/publishers — Live publisher directory with heartbeat tracking.
"""

import time
import threading

class PublisherRegistry:
    def __init__(self, heartbeat_timeout: float = 30.0):
        self._pub: dict[str, dict] = {}
        self._timeout = heartbeat_timeout
        self._lock = threading.Lock()

    def register(self, pub_id: str, namespace: str, ws=None, metadata: dict = None):
        with self._lock:
            self._pub[pub_id] = {
                'namespace':     namespace,
                'ws':            ws,
                'metadata':      metadata or {},
                'registered_at': time.time(),
                'last_heartbeat': time.time(),
                'frame_count':   0,
            }

    def heartbeat(self, pub_id: str):
        with self._lock:
            if pub_id in self._pub:
                self._pub[pub_id]['last_heartbeat'] = time.time()

    def increment(self, pub_id: str):
        with self._lock:
            if pub_id in self._pub:
                self._pub[pub_id]['frame_count'] += 1

    def unregister(self, pub_id: str):
        with self._lock:
            self._pub.pop(pub_id, None)

    def is_alive(self, pub_id: str) -> bool:
        p = self._pub.get(pub_id)
        if not p:
            return False
        return (time.time() - p['last_heartbeat']) < self._timeout

    def stale(self) -> list[str]:
        return [pid for pid in self._pub if not self.is_alive(pid)]

    def all(self) -> dict:
        with self._lock:
            return {k: {**v, 'ws': None} for k, v in self._pub.items()}

    def namespace_of(self, pub_id: str) -> str | None:
        return self._pub.get(pub_id, {}).get('namespace')

publishers = PublisherRegistry()
