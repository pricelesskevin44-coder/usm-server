"""
core/harmonics — Wave-2 Emotional Physics Layer
Derives resonance, tension, drift, coherence from consecutive state snapshots.
"""

from core.schema import HarmonicsMetadata
import math

def compute_harmonics(
    prev: dict,
    curr: dict,
    prev_harmonics: HarmonicsMetadata | None = None,
) -> HarmonicsMetadata:
    all_keys     = set(prev) | set(curr)
    total        = max(len(all_keys), 1)
    changed_keys = [k for k in all_keys if curr.get(k) != prev.get(k)]
    num_changed  = len(changed_keys)

    # Resonance: fraction of keys that stayed the same
    resonance = 1.0 - (num_changed / total)

    # Tension: normalized change pressure
    tension = num_changed / total

    # Drift: sum of numeric deltas normalized by count
    numeric_drift = 0.0
    numeric_count = 0
    for k in changed_keys:
        cv, pv = curr.get(k, 0), prev.get(k, 0)
        if isinstance(cv, (int, float)) and isinstance(pv, (int, float)):
            numeric_drift += abs(cv - pv)
            numeric_count += 1
    drift = numeric_drift / max(numeric_count, 1)

    # Coherence: inverse log of drift, bounded 0-1
    coherence = max(0.0, 1.0 - math.log1p(drift) / 10.0)

    # Smooth with previous harmonics if available (EMA α=0.3)
    if prev_harmonics:
        a = 0.3
        resonance = a * resonance + (1 - a) * prev_harmonics.resonance
        tension   = a * tension   + (1 - a) * prev_harmonics.tension
        coherence = a * coherence + (1 - a) * prev_harmonics.coherence

    return HarmonicsMetadata(
        resonance=round(resonance, 6),
        tension=round(tension, 6),
        drift=round(drift, 6),
        coherence=round(coherence, 6),
    )
