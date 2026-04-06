"""
registry/namespaces — Dynamic namespace lifecycle, ownership, and metadata.
"""

import time
import threading

class NamespaceRegistry:
    def __init__(self):
        self._ns:   dict[str, dict] = {}
        self._lock = threading.Lock()

    def declare(self, namespace: str, owner_id: str = "", metadata: dict = None):
        with self._lock:
            if namespace not in self._ns:
                self._ns[namespace] = {
                    'owner_id':   owner_id,
                    'created_at': time.time(),
                    'updated_at': time.time(),
                    'metadata':   metadata or {},
                    'frame_count': 0,
                }
            else:
                self._ns[namespace]['updated_at'] = time.time()
                self._ns[namespace]['frame_count'] += 1

    def exists(self, namespace: str) -> bool:
        return namespace in self._ns

    def owner(self, namespace: str) -> str:
        return self._ns.get(namespace, {}).get('owner_id', '')

    def all(self) -> list[str]:
        return list(self._ns.keys())

    def info(self, namespace: str) -> dict:
        return dict(self._ns.get(namespace, {}))

    def hierarchy(self, namespace: str) -> list[str]:
        parts = namespace.split('/')
        return ['/'.join(parts[:i+1]) for i in range(len(parts))]

    def remove(self, namespace: str):
        with self._lock:
            self._ns.pop(namespace, None)

    def stats(self) -> dict:
        return {
            'total_namespaces': len(self._ns),
            'namespaces': {k: v['frame_count'] for k, v in self._ns.items()},
        }

namespaces = NamespaceRegistry()
