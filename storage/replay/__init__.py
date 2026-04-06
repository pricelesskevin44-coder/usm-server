"""
storage/replay — Frame replay engine: last-N, since-timestamp, range queries.
"""

import os
from storage.disk import disk

class ReplayEngine:
    def last_n(self, namespace: str, n: int, date: str = None) -> list:
        files = disk.list_frames(namespace, date)[-n:]
        return [disk.load_frame(f) for f in files]

    def since(self, namespace: str, since_ts: float, date: str = None) -> list:
        files = [
            f for f in disk.list_frames(namespace, date)
            if float(os.path.basename(f).replace('.json', '')) >= since_ts
        ]
        return [disk.load_frame(f) for f in files]

    def between(self, namespace: str, start_ts: float, end_ts: float) -> list:
        files = [
            f for f in disk.list_frames(namespace)
            if start_ts <= float(os.path.basename(f).replace('.json', '')) <= end_ts
        ]
        return [disk.load_frame(f) for f in files]

replay = ReplayEngine()
