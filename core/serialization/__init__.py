"""
core/serialization — StateFrame encode/decode.
decode_json_frame never raises on structurally valid JSON —
unknown keys are stripped, missing keys use dataclass defaults.
"""

import json
from core.schema import (
    StateFrame, HarmonicsMetadata, TemporalMetadata,
    BinaryDescriptor, FRAME_VERSION
)

_FRAME_FIELDS = set(StateFrame.__dataclass_fields__.keys())

def encode_json_frame(frame: StateFrame) -> bytes:
    d = _to_dict(frame)
    return json.dumps(d, default=str).encode('utf-8')

def _to_dict(frame: StateFrame) -> dict:
    from dataclasses import asdict
    d = asdict(frame)
    blob = d.get('binary_blob')
    if isinstance(blob, (bytes, bytearray)):
        d['binary_blob'] = list(blob)
    return d

def decode_json_frame(data: bytes | str) -> StateFrame:
    if isinstance(data, (bytes, bytearray)):
        data = data.decode('utf-8')
    raw = json.loads(data)

    # Rebuild sub-objects safely
    h = raw.get('harmonics', {})
    t = raw.get('temporal', {})
    b = raw.get('binary_desc', {})

    if not isinstance(h, dict): h = {}
    if not isinstance(t, dict): t = {}
    if not isinstance(b, dict): b = {}

    harmonics   = HarmonicsMetadata(**{
        k: v for k, v in h.items()
        if k in HarmonicsMetadata.__dataclass_fields__
    })
    temporal    = TemporalMetadata(**{
        k: v for k, v in t.items()
        if k in TemporalMetadata.__dataclass_fields__
    })
    binary_desc = BinaryDescriptor(**{
        k: v for k, v in b.items()
        if k in BinaryDescriptor.__dataclass_fields__
    })

    # Reconstruct binary_blob
    blob = raw.get('binary_blob')
    if isinstance(blob, list):
        blob = bytes(blob)
    elif not isinstance(blob, (bytes, bytearray, type(None))):
        blob = None

    # Build kwargs — only known StateFrame fields, rest discarded
    kwargs = {
        'namespace':    raw.get('namespace', ''),
        'frame_type':   raw.get('frame_type', 'state'),
        'json_state':   raw.get('json_state', {}),
        'binary_blob':  blob,
        'harmonics':    harmonics,
        'temporal':     temporal,
        'binary_desc':  binary_desc,
        'version':      raw.get('version', FRAME_VERSION),
        'publisher_id': raw.get('publisher_id', ''),
        'error_msg':    raw.get('error_msg', ''),
    }

    return StateFrame(**kwargs)
