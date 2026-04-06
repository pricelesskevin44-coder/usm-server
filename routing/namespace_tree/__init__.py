"""
routing/namespace_tree — Dynamic namespace registry and live hierarchy tree.
"""

import threading

class NamespaceTree:
    def __init__(self):
        self._tree: dict = {}
        self._lock = threading.Lock()

    def register(self, namespace: str, metadata: dict = None):
        parts = namespace.split('/')
        with self._lock:
            node = self._tree
            for part in parts:
                node = node.setdefault(part, {})
            node['__meta__'] = metadata or {}

    def exists(self, namespace: str) -> bool:
        parts = namespace.split('/')
        node  = self._tree
        for part in parts:
            if part not in node:
                return False
            node = node[part]
        return True

    def children(self, namespace: str) -> list[str]:
        parts = namespace.split('/')
        node  = self._tree
        for part in parts:
            node = node.get(part, {})
        return [k for k in node if k != '__meta__']

    def all_namespaces(self) -> list[str]:
        results = []
        def _walk(node, prefix):
            for k, v in node.items():
                if k == '__meta__':
                    continue
                path = f"{prefix}/{k}" if prefix else k
                if '__meta__' in v:
                    results.append(path)
                _walk(v, path)
        _walk(self._tree, '')
        return results

    def remove(self, namespace: str):
        parts = namespace.split('/')
        with self._lock:
            def _del(node, parts):
                if not parts:
                    return
                head, *tail = parts
                if head not in node:
                    return
                if not tail:
                    del node[head]
                else:
                    _del(node[head], tail)
            _del(self._tree, parts)

tree = NamespaceTree()   # module-level singleton
