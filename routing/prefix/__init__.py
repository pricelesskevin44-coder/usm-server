"""
routing/prefix — Hierarchical prefix subscription matching.
'robot/alpha' prefix matches 'robot/alpha/perception/depth'
"""

def matches_prefix(namespace: str, pattern: str) -> bool:
    clean = pattern.rstrip('/')
    return namespace == clean or namespace.startswith(clean + '/')
