"""
ws/handshake — Handshake protocol.

Client sends as FIRST message:
  Publisher: {"frame_type":"handshake","role":"publisher","version":1}
  Viewer:    {"frame_type":"handshake","role":"viewer","version":1,"subscription":"#"}

Namespace (publisher) and subscription (viewer) are also accepted
from URL path as fallback:
  /publish/<namespace>
  /view/<pattern>
"""

import uuid
import json
from core.versioning import negotiate, make_handshake_payload
from ws.frames       import build_error

async def perform_handshake(websocket) -> dict | None:
    try:
        raw = await websocket.recv()
        hs  = json.loads(raw)
    except Exception as e:
        try:
            await websocket.send(build_error("handshake_failed", str(e)))
        except Exception:
            pass
        return None

    if hs.get('frame_type') != 'handshake':
        try:
            await websocket.send(
                build_error("bad_handshake", "First message must be handshake frame")
            )
        except Exception:
            pass
        return None

    try:
        version = negotiate(int(hs.get('version', 1)))
    except ValueError as e:
        try:
            await websocket.send(build_error("version_mismatch", str(e)))
        except Exception:
            pass
        return None

    client_id        = hs.get('id') or str(uuid.uuid4())[:8]
    hs['id']         = client_id
    hs['version']    = version

    ack              = make_handshake_payload(version)
    ack['client_id'] = client_id
    try:
        await websocket.send(json.dumps(ack).encode())
    except Exception:
        return None

    return hs
