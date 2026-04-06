"""
routing/wildcard — Single-level (*) and multi-level (#) wildcard matching.

Patterns:
  robot/*/perception     matches  robot/alpha/perception  (single-level *)
  robot/#                matches  robot/alpha/perception/depth  (multi-level #)
  *                      matches  any single-segment namespace
"""

def matches_wildcard(namespace: str, pattern: str) -> bool:
    ns_parts  = namespace.split('/')
    pat_parts = pattern.split('/')

    # Multi-level wildcard: # matches everything from that point forward
    if '#' in pat_parts:
        idx = pat_parts.index('#')
        if idx == 0:
            return True   # pure '#' matches everything
        return ns_parts[:idx] == pat_parts[:idx]

    # Single-level: must be same depth
    if len(ns_parts) != len(pat_parts):
        return False

    return all(p == '*' or p == n for p, n in zip(pat_parts, ns_parts))
