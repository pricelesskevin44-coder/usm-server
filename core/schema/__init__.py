"""
core/schema — Universal State Format (USM canonical frame definition)
Every byte that flows through USM is wrapped in a StateFrame.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Literal

FRAME_VERSION = 1

FrameType = Literal["state", "heartbeat", "handshake", "error", "replay", "meta"]

@dataclass
class HarmonicsMetadata:
    resonance: float = 0.0   # 0-1: stability between frames
    tension:   float = 0.0   # 0-1: rate of change pressure
    drift:     float = 0.0   # cumulative deviation magnitude
    coherence: float = 1.0   # 0-1: internal consistency score

@dataclass
class TemporalMetadata:
    timestamp:   float = 0.0   # Unix epoch (seconds)
    delta:       float = 0.0   # seconds since last frame
    momentum:    float = 0.0   # rate-of-change magnitude
    frame_index: int   = 0     # monotonic per-namespace counter

@dataclass
class BinaryDescriptor:
    present:    bool   = False
    byte_count: int    = 0
    media_type: str    = "application/octet-stream"   # image/jpeg, audio/raw, etc.
    encoding:   str    = "raw"                         # raw | base64 | zlib

@dataclass
class StateFrame:
    namespace:   str
    frame_type:  FrameType           = "state"
    json_state:  dict                = field(default_factory=dict)
    binary_blob: Optional[bytes]     = None
    harmonics:   HarmonicsMetadata   = field(default_factory=HarmonicsMetadata)
    temporal:    TemporalMetadata    = field(default_factory=TemporalMetadata)
    binary_desc: BinaryDescriptor    = field(default_factory=BinaryDescriptor)
    version:     int                 = FRAME_VERSION
    publisher_id: str                = ""
    error_msg:    str                = ""

    def validate(self) -> list[str]:
        """Return list of validation errors, empty = valid."""
        errors = []
        if not self.namespace:
            errors.append("namespace is required")
        if '\\' in self.namespace:
            errors.append("namespace must use forward slashes only")
        if self.version != FRAME_VERSION:
            errors.append(f"unsupported version {self.version}")
        if self.binary_blob and not self.binary_desc.present:
            errors.append("binary_blob present but binary_desc.present=False")
        return errors
