"""
ws/pairing — Pairs JSON + binary + harmonics + temporal into a unified StateFrame.
"""

from core.schema       import StateFrame, HarmonicsMetadata, TemporalMetadata
from core.harmonics    import compute_harmonics
from core.temporal     import TemporalTracker

_trackers: dict[str, TemporalTracker] = {}

def pair(
    namespace: str,
    json_state: dict,
    binary_blob: bytes = None,
    prev_state:  dict  = None,
) -> StateFrame:
    if namespace not in _trackers:
        _trackers[namespace] = TemporalTracker()
    temporal  = _trackers[namespace].stamp()
    harmonics = compute_harmonics(prev_state or {}, json_state)
    return StateFrame(
        namespace=namespace,
        json_state=json_state,
        binary_blob=binary_blob,
        harmonics=harmonics,
        temporal=temporal,
    )
