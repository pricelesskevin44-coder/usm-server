"""
core/versioning — Protocol version negotiation + handshake.
"""

from core.schema import FRAME_VERSION

SUPPORTED = {1}

def negotiate(client_version: int) -> int:
    if client_version in SUPPORTED:
        return client_version
    # Offer our highest supported
    best = max(SUPPORTED)
    raise ValueError(
        f"Client requested version {client_version}; "
        f"server supports {sorted(SUPPORTED)}. Use version {best}."
    )

def make_handshake_payload(accepted_version: int) -> dict:
    return {
        "type": "handshake_ack",
        "accepted_version": accepted_version,
        "server_version": FRAME_VERSION,
        "supported": sorted(SUPPORTED),
    }
