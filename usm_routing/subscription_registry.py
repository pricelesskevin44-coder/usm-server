class SubscriptionRegistry:
    def __init__(self):
        self.subs = {}  # pattern -> set(websockets)

    def subscribe(self, ws, pattern):
        if pattern not in self.subs:
            self.subs[pattern] = set()
        self.subs[pattern].add(ws)

    def unsubscribe(self, ws):
        for subs in self.subs.values():
            subs.discard(ws)

    def match(self, namespace):
        matched = set()
        for pattern, sockets in self.subs.items():
            if pattern == "#" or namespace.startswith(pattern):
                matched.update(sockets)
        return matched
