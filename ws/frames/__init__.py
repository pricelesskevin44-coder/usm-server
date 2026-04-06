"""
ws/frames — Frame type definitions, encoding, decoding.
parse_frame() catches all decode errors and returns an error dict
instead of raising — one bad frame never kills a connection.
"""

import json
import time
from core.schema import StateFrame
from core.serialization import encode_json_frame, decode_json_frame

def build_state_frame(frame: StateFrame) -> bytes:
    return encode_json_frame(frame)

def build_heartbeat(sender_id: str) -> bytes:
    return json.dumps({
        "frame_type": "heartbeat",
        "sender_id":  sender_id,
        "ts":         time.time(),
    }).encode()

def build_error(code: str, message: str) -> bytes:
    return json.dumps({
        "frame_type": "error",
        "code":       code,
        "message":    message,
        "ts":         time.time(),
    }).encode()

def build_handshake_ack(version: int) -> bytes:
    from core.versioning import make_handshake_payload
    return json.dumps(make_handshake_payload(version)).encode()

def build_meta_frame(namespace: str, metadata: dict) -> bytes:
    return json.dumps({
        "frame_type": "meta",
        "namespace":  namespace,
        "metadata":   metadata,
        "ts":         time.time(),
    }).encode()

def parse_frame(raw) -> StateFrame | dict:
    """
    Parse raw WebSocket message.
    Returns StateFrame for state frames, dict for control frames.
    Never raises — returns error dict on decode failure.
    """
    # Pure binary blob
    if isinstance(raw, (bytes, bytearray)):
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            return {'frame_type': '__binary__', 'raw': raw}
    else:
        text = raw

    try:
        d = json.loads(text)
    except json.JSONDecodeError as e:
        return {'frame_type': 'error', 'code': 'json_decode', 'message': str(e)}

    ft = d.get('frame_type', 'state')

    if ft == 'state':
        try:
            return decode_json_frame(text)
        except Exception as e:
            return {'frame_type': 'error', 'code': 'frame_decode', 'message': str(e), '_raw': d}

    return d
