"""
storage/memory — Live in-RAM state store (latest frame per namespace).
"""

import threading
from core.schema import StateFrame

class MemoryStore:
    def __init__(self):
        self._store: dict[str, StateFrame] = {}
        self._lock  = threading.Lock()

    def write(self, frame: StateFrame):
        with self._lock:
            self._store[frame.namespace] = frame

    def read(self, namespace: str) -> StateFrame | None:
        return self._store.get(namespace)

    def all_namespaces(self) -> list[str]:
        return list(self._store.keys())

    def snapshot(self) -> dict[str, StateFrame]:
        with self._lock:
            return dict(self._store)

    def delete(self, namespace: str):
        with self._lock:
            self._store.pop(namespace, None)

mem = MemoryStore()
