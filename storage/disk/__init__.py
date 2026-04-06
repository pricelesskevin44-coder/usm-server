"""
storage/disk — Timestamped persistent frame storage.
Layout:
  {base}/{namespace}/{YYYY-MM-DD}/{ts:.6f}.json
  {base}/{namespace}/{YYYY-MM-DD}/{ts:.6f}.bin   (if binary)
"""

import os
import json
import time
from datetime import datetime
from dataclasses import asdict
from core.schema import StateFrame, HarmonicsMetadata, TemporalMetadata, BinaryDescriptor

DEFAULT_BASE = os.path.join(os.path.expanduser("~"), "usm_data")

class DiskStore:
    def __init__(self, base_path: str = DEFAULT_BASE):
        self.base = base_path
        os.makedirs(self.base, exist_ok=True)

    def _frame_dir(self, namespace: str) -> str:
        safe  = namespace.replace('/', '__')
        today = datetime.utcnow().strftime('%Y-%m-%d')
        path  = os.path.join(self.base, safe, today)
        os.makedirs(path, exist_ok=True)
        return path

    def write(self, frame: StateFrame):
        ts   = frame.temporal.timestamp or time.time()
        dir_ = self._frame_dir(frame.namespace)
        d    = asdict(frame)
        blob = d.pop('binary_blob', None)
        d['binary_blob'] = None
        with open(os.path.join(dir_, f"{ts:.6f}.json"), 'w') as f:
            json.dump(d, f, default=str)
        if blob:
            bdata = bytes(blob) if isinstance(blob, list) else blob
            with open(os.path.join(dir_, f"{ts:.6f}.bin"), 'wb') as f:
                f.write(bdata)

    def list_frames(self, namespace: str, date: str = None) -> list[str]:
        safe  = namespace.replace('/', '__')
        day   = date or datetime.utcnow().strftime('%Y-%m-%d')
        dir_  = os.path.join(self.base, safe, day)
        if not os.path.isdir(dir_):
            return []
        return sorted(
            os.path.join(dir_, f)
            for f in os.listdir(dir_)
            if f.endswith('.json')
        )

    def load_frame(self, path: str) -> StateFrame:
        with open(path) as f:
            d = json.load(f)
        d['harmonics']   = HarmonicsMetadata(**d.get('harmonics', {}))
        d['temporal']    = TemporalMetadata(**d.get('temporal', {}))
        d['binary_desc'] = BinaryDescriptor(**d.get('binary_desc', {}))
        d['binary_blob'] = None
        bin_path = path.replace('.json', '.bin')
        if os.path.exists(bin_path):
            with open(bin_path, 'rb') as f:
                d['binary_blob'] = f.read()
        return StateFrame(**{k: d[k] for k in StateFrame.__dataclass_fields__})

disk = DiskStore()
