"""
routing/matcher — Master subscription matching engine.
"""

from routing.wildcard import matches_wildcard
from routing.prefix   import matches_prefix
import threading

class RoutingEngine:
    def __init__(self):
        self._subs: dict[str, list[str]] = {}
        self._lock = threading.Lock()

    def subscribe(self, viewer_id: str, pattern: str):
        with self._lock:
            self._subs.setdefault(viewer_id, [])
            if pattern not in self._subs[viewer_id]:
                self._subs[viewer_id].append(pattern)
        logger_msg(f"[ROUTER] subscribe viewer={viewer_id} pattern={pattern}")

    def unsubscribe(self, viewer_id: str, pattern: str = None):
        with self._lock:
            if pattern is None:
                self._subs.pop(viewer_id, None)
            else:
                subs = self._subs.get(viewer_id, [])
                self._subs[viewer_id] = [s for s in subs if s != pattern]

    def resolve(self, namespace: str) -> list[str]:
        """Return viewer_ids whose subscription patterns match namespace."""
        matches = []
        with self._lock:
            subs_snapshot = dict(self._subs)
        for viewer_id, patterns in subs_snapshot.items():
            for pat in patterns:
                if _match(namespace, pat):
                    matches.append(viewer_id)
                    break
        return matches

    def all_subscriptions(self) -> dict:
        with self._lock:
            return dict(self._subs)

def _match(namespace: str, pattern: str) -> bool:
    """Try exact, wildcard, prefix — in that order."""
    if namespace == pattern:
        return True
    if matches_wildcard(namespace, pattern):
        return True
    if matches_prefix(namespace, pattern):
        return True
    return False

def logger_msg(msg: str):
    try:
        from utils.logging import logger
        logger.debug(msg)
    except Exception:
        pass

router = RoutingEngine()
