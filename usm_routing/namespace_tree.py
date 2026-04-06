class NamespaceNode:
    def __init__(self):
        self.children = {}
        self.subscribers = set()

class NamespaceTree:
    def __init__(self):
        self.root = NamespaceNode()

    def _split(self, namespace):
        return namespace.strip("/").split("/")

    def add_subscriber(self, namespace, subscriber):
        node = self.root
        for part in self._split(namespace):
            if part not in node.children:
                node.children[part] = NamespaceNode()
            node = node.children[part]
        node.subscribers.add(subscriber)

    def remove_subscriber(self, namespace, subscriber):
        node = self.root
        for part in self._split(namespace):
            if part not in node.children:
                return
            node = node.children[part]
        node.subscribers.discard(subscriber)

    def match(self, namespace):
        matched = set()
        parts = self._split(namespace)

        def recurse(node, idx):
            if "#" in node.children:
                matched.update(node.children["#"].subscribers)
            if idx == len(parts):
                matched.update(node.subscribers)
                return
            part = parts[idx]
            if "*" in node.children:
                recurse(node.children["*"], idx + 1)
            if part in node.children:
                recurse(node.children[part], idx + 1)

        recurse(self.root, 0)
        return matched
