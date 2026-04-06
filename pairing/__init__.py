"""
pairing — JSON + Binary frame pairing engine.
Publishers send JSON and binary frames independently.
This engine matches them by namespace + frame_index within a timeout window.
"""

import time
import threading
from core.schema import StateFrame, BinaryDescriptor
from core.harmonics import compute_harmonics
from core.temporal  import stamp_namespace

PAIR_TIMEOUT = 2.0   # seconds to wait for binary partner

class PairingEngine:
    def __init__(self, timeout: float = PAIR_TIMEOUT):
        self._timeout  = timeout
        self._json_q:   dict[str, dict] = {}   # key -> {frame, ts}
        self._binary_q: dict[str, dict] = {}   # key -> {blob, desc, ts}
        self._prev_state: dict[str, dict] = {} # namespace -> last json_state
        self._prev_harmonics = {}
        self._lock = threading.Lock()

    def _key(self, namespace: str, frame_index: int) -> str:
        return f"{namespace}::{frame_index}"

    def ingest_json(self, frame: StateFrame) -> StateFrame | None:
        """
        Accept a JSON-only frame. If a binary partner is waiting, pair them.
        Otherwise queue and return None (will be released on pairing or timeout).
        If no binary_blob is expected (binary_desc.present=False), emit immediately.
        """
        self._enrich(frame)

        if not frame.binary_desc.present:
            self._update_prev(frame)
            return frame   # no binary partner needed

        key = self._key(frame.namespace, frame.temporal.frame_index)
        with self._lock:
            if key in self._binary_q:
                entry = self._binary_q.pop(key)
                return self._merge(frame, entry['blob'], entry['desc'])
            self._json_q[key] = {'frame': frame, 'ts': time.time()}
        return None

    def ingest_binary(self, namespace: str, blob: bytes,
                      desc: BinaryDescriptor, frame_index: int) -> StateFrame | None:
        """Accept a raw binary blob. If JSON partner is waiting, pair them."""
        key = self._key(namespace, frame_index)
        with self._lock:
            if key in self._json_q:
                entry = self._json_q.pop(key)
                merged = self._merge(entry['frame'], blob, desc)
                return merged
            self._binary_q[key] = {'blob': blob, 'desc': desc, 'ts': time.time()}
        return None

    def flush_stale(self) -> list[StateFrame]:
        """Release JSON frames whose binary partner never arrived (timeout)."""
        now     = time.time()
        flushed = []
        with self._lock:
            stale_keys = [k for k, v in self._json_q.items()
                          if now - v['ts'] > self._timeout]
            for k in stale_keys:
                entry = self._json_q.pop(k)
                frame = entry['frame']
                frame.error_msg = "binary_pair_timeout"
                flushed.append(frame)
        return flushed

    def _enrich(self, frame: StateFrame):
        """Stamp temporal and compute harmonics in-place."""
        frame.temporal = stamp_namespace(frame.namespace)
        prev = self._prev_state.get(frame.namespace, {})
        prev_h = self._prev_harmonics.get(frame.namespace)
        frame.harmonics = compute_harmonics(prev, frame.json_state, prev_h)

    def _merge(self, frame: StateFrame, blob: bytes, desc: BinaryDescriptor) -> StateFrame:
        frame.binary_blob = blob
        frame.binary_desc = desc
        frame.binary_desc.present   = True
        frame.binary_desc.byte_count = len(blob)
        self._update_prev(frame)
        return frame

    def _update_prev(self, frame: StateFrame):
        self._prev_state[frame.namespace]     = dict(frame.json_state)
        self._prev_harmonics[frame.namespace] = frame.harmonics

pairing = PairingEngine()
