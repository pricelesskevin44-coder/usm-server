"""
core/temporal — Per-namespace timestamp, delta, momentum tracking.
"""

import time
from core.schema import TemporalMetadata

class TemporalTracker:
    def __init__(self):
        self._last_ts:    float = 0.0
        self._last_delta: float = 0.0
        self._frame_idx:  int   = 0

    def stamp(self) -> TemporalMetadata:
        now      = time.time()
        delta    = (now - self._last_ts) if self._last_ts else 0.0
        momentum = abs(delta - self._last_delta)
        self._last_delta = delta
        self._last_ts    = now
        self._frame_idx += 1
        return TemporalMetadata(
            timestamp=now,
            delta=round(delta, 6),
            momentum=round(momentum, 6),
            frame_index=self._frame_idx,
        )

# Global per-namespace tracker pool
_trackers: dict[str, TemporalTracker] = {}

def stamp_namespace(namespace: str) -> TemporalMetadata:
    if namespace not in _trackers:
        _trackers[namespace] = TemporalTracker()
    return _trackers[namespace].stamp()
