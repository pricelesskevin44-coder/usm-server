"""
registry/viewers — Live viewer directory: subscriptions, heartbeats, cleanup.
"""

import time
import threading

class ViewerRegistry:
    def __init__(self, heartbeat_timeout: float = 30.0):
        self._viewers: dict[str, dict] = {}
        self._timeout = heartbeat_timeout
        self._lock = threading.Lock()

    def register(self, viewer_id: str, ws=None, subscription: str = '#'):
        with self._lock:
            self._viewers[viewer_id] = {
                'ws':            ws,
                'subscription':  subscription,
                'is_wildcard':   '*' in subscription,
                'is_prefix':     '#' in subscription,
                'registered_at': time.time(),
                'last_heartbeat': time.time(),
                'frames_received': 0,
            }

    def heartbeat(self, viewer_id: str):
        with self._lock:
            if viewer_id in self._viewers:
                self._viewers[viewer_id]['last_heartbeat'] = time.time()

    def increment(self, viewer_id: str):
        with self._lock:
            if viewer_id in self._viewers:
                self._viewers[viewer_id]['frames_received'] += 1

    def unregister(self, viewer_id: str):
        with self._lock:
            self._viewers.pop(viewer_id, None)

    def is_alive(self, viewer_id: str) -> bool:
        v = self._viewers.get(viewer_id)
        if not v:
            return False
        return (time.time() - v['last_heartbeat']) < self._timeout

    def stale(self) -> list[str]:
        return [vid for vid in self._viewers if not self.is_alive(vid)]

    def ws_of(self, viewer_id: str):
        return self._viewers.get(viewer_id, {}).get('ws')

    def all(self) -> dict:
        with self._lock:
            return {k: {**v, 'ws': None} for k, v in self._viewers.items()}

viewers = ViewerRegistry()
