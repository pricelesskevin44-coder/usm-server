"""
utils/errors — Standardized USM error taxonomy.
"""

class USMError(Exception):
    code = "usm_error"

class NamespaceError(USMError):
    code = "namespace_error"

class VersionError(USMError):
    code = "version_error"

class FrameDecodeError(USMError):
    code = "frame_decode_error"

class StorageError(USMError):
    code = "storage_error"

class RoutingError(USMError):
    code = "routing_error"

class PairingError(USMError):
    code = "pairing_error"

class HandshakeError(USMError):
    code = "handshake_error"

class ValidationError(USMError):
    code = "validation_error"
